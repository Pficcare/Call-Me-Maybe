*This project has been created as part of the 42 curriculum by pficcare.*

# call me maybe

## Description

This project translates a request written in natural language into a function call. Given "What is the sum of 2 and 3?", the program does not answer 5. It finds the function to call and its arguments:

```
fn_add_numbers {"a": 2.0, "b": 3.0}
```

The language model is Qwen3-0.6B, a very small model that often produces broken JSON when it writes freely. The program therefore uses **constrained decoding**: at each step, the tokens that would break the expected format are forbidden. The model chooses, but only among valid tokens.

### Project status

| Part | State |
|---|---|
| Reading and validating the input files | done |
| Choosing the function | done |
| Extracting `number`, `integer`, `boolean` and `string` arguments | done |
| Writing the output file (`--output`) | done |
| Unit tests (`make test`) | value rules done, other modules not yet |

## Instructions

Requirements: Python 3.10 or later and [uv](https://docs.astral.sh/uv/). The model is downloaded on the first run.

| Command | Effect |
|---|---|
| `make install` | install the dependencies (`uv sync`) |
| `make run` | run the program |
| `make run ARGS="--input my_file.json"` | run it with options |
| `make debug` | run it with pdb |
| `make test` | run the unit tests (pytest, without the model) |
| `make lint` | run flake8 and mypy |
| `make clean` | remove the caches |

The program can also be started directly:

```sh
uv run python -m src [--functions_definition FILE] [--input FILE] [--output FILE] [--model NAME]
```

| Option | Default value |
|---|---|
| `--functions_definition` | `data/input/functions_definition.json` |
| `--input` | `data/input/function_calling_tests.json` |
| `--output` | `data/output/function_calling_results.json` |
| `--model` | `Qwen/Qwen3-0.6B` |

### Source files

| File | Role |
|---|---|
| `src/__main__.py` | calls the other modules, handles errors and exit codes |
| `src/arguments.py` | command line options |
| `src/schemas.py` | pydantic models of the input and output data |
| `src/json_io.py` | reads, checks and writes JSON files |
| `src/llm.py` | every call to `llm_sdk` |
| `src/tokens.py` | builds the table that gives the text of each token |
| `src/prompts.py` | builds the two texts given to the model |
| `src/rules.py` | says if a text is, or can become, a valid value |
| `src/decoder.py` | masks the logits and generates a name or a value |
| `src/generator.py` | handles each request: function, then arguments |
| `tests/` | unit tests, run with `make test` |
| `scripts/explore_model.py` | demonstration of tokens, logits and generation without constraint |

## Example usage

```sh
uv run python -m src
```

Part of the output:

```
Prompt: 'What is the sum of 265 and 345?'
  -> fn_add_numbers
  -> {'a': 265.0, 'b': 345.0}

Prompt: "Reverse the string 'hello'"
  -> fn_reverse_string
  -> {'s': 'hello'}

Prompt: 'Replace all numbers in "Hello 34 I\'m 233 years old" with NUMBERS'
  -> fn_substitute_string_with_regex
  -> {'source_string': "Hello 34 I'm 233 years old", 'regex': '[0-9]+', 'replacement': 'NUMBERS'}

11 function calls written to data/output/function_calling_results.json
```

The first entry of the output file:

```json
{
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {
        "a": 2.0,
        "b": 3.0
    }
}
```

With a missing file, the program stops with exit code 1 and a message:

```
Error: Cannot read 'missing.json': [Errno 2] No such file or directory: 'missing.json'
```

## Algorithm explanation

### One constrained step

1. Encode the text into token ids and ask the model for the logits: one score per token.
2. For each token of the vocabulary, look at `current value + token text`. If it can still become a valid value, the token is allowed.
3. Set the logits of all the other tokens to minus infinity.
4. Take the allowed token with the highest score, add it to the value, and start again.

The text of each token comes from the model's vocabulary file. That file uses the GPT-2 byte encoding, where for example a space is written `Ġ`, so `src/tokens.py` converts it back to real text. Tokens that are not valid UTF-8 alone are left out. The table has 150195 tokens.

### The prompts

Qwen3 was trained on conversations marked with special tokens. Both prompts use this chat format: the request is in the user turn, and the beginning of the answer is already written in the assistant turn, so the model continues it.

```
<|im_start|>user
Available functions:
- fn_add_numbers(a: number, b: number): Add two numbers together and return their sum.
...

Request: What is the sum of 2 and 3?
Answer with the function call in JSON.<|im_end|>
<|im_start|>assistant
<think>

</think>

{"name": "
```

The empty `<think>` block is the official way to turn off the reasoning mode of Qwen3. Without it, the model would want to write `<think>` first, which the masks forbid.

### Choosing the function

The allowed tokens are those that continue one of the function names. Once the text is a complete name, any token starting with `"` ends the choice. The model makes the choice, but it cannot write a name that does not exist. As soon as only one name matches the text already generated, the model has nothing left to decide, so the program stops calling it.

### Extracting the arguments

The program writes all the fixed JSON itself: braces, keys, colons, commas and quotes. The model only generates the values:

```
{"a": 2 ,"b": 3 }
 ^^^^^  ^^^^^   ^    written by the program
       ^      ^      generated by the model
```

(The spaces are only there to make the drawing readable.)

Each type has three rules:

| Rule | Question | `number` | `integer` | `boolean` | `string` |
|---|---|---|---|---|---|
| prefix | can this text become a valid value? | a beginning of a number | a beginning of an integer | a beginning of `true` or `false` | no `"`, no `\`, no control character |
| complete | is it already a valid value? | a full number (JSON grammar, leading zeros allowed) | a full integer (leading zeros allowed) | `true` or `false` | same as prefix |
| end | does this token finish the value? | starts with `,` or `}` | same as `number` | same as `number` | starts with `"` |

An end token is allowed only if the value is complete: after `2.`, the model cannot stop. The end token is thrown away, since the program writes the punctuation. The JSON is therefore valid whatever the model chose.

A number prefix is checked with one trick: an unfinished number always lacks a digit. If `text + "0"` is a complete number, `text` is a valid beginning (`-`, `1.`, `1e`).

JSON forbids leading zeros (`05`), but the rules accept them: otherwise the model can be trapped (see "Challenges faced"). The zeros are removed before the value is inserted in the JSON text, so `05` becomes `5`.

A value is limited to 100 tokens, so the generation always stops.

## Design decisions

| Decision | Reason |
|---|---|
| Two steps: function first, arguments next | the second prompt describes only one function, so it is shorter and faster (39 tokens instead of 138 in our measures) |
| The full text is encoded again before each value | two texts encoded separately do not always give the same tokens as the whole text |
| No space after `:` | see "Challenges faced" |
| Any token starting with `"`, `,` or `}` can end a value, and any token starting with `"` can end a function name | see "Challenges faced" |
| JSON number grammar, with `[0-9]` and not `\d` | `\d` also accepts other Unicode digits such as `２`, which are in the vocabulary but not valid in JSON |
| Leading zeros accepted, then removed | the model can write `05` for 5; the JSON text stays valid |
| Chat format of Qwen in both prompts, built by one function (`build_chat_prompt`) | clearly better than raw text (see "Performance analysis"); another model only needs this function to change |
| No instruction sentence added to the prompts | each sentence we tried made the results worse |
| `"` and `\` are forbidden inside strings | no escape sequence to handle, but a value cannot contain them (no `\d` in a generated regex) |
| `llm_sdk` is imported only when the model is loaded | an error in the input files is reported without waiting for torch |
| A JSON file with invalid Unicode is refused when it is read | one check covers prompts, descriptions and parameter names |
| A request that fails is reported on stderr and left out of the output file | one bad request does not stop the others, and every entry of the file follows the schema |
| `number` values are converted to float, and refused if they are too large | the subject shows `2.0`, and `inf` is not valid JSON |

## Performance analysis

Measured on the 11 prompts of the subject, on a CPU (Intel Core Ultra 7 155H):

| Measure | Result |
|---|---|
| Correct function | 11/11 |
| Valid JSON, with the keys and types of the schema | 11/11 |
| Exactly correct arguments | 11/11 |
| Total time | 116 to 131 s in five runs (limit: 300 s) |

The three regex results were also checked by applying them: for example `[aeiouAEIOU]` with `*` gives `Pr*gr*mm*ng *s f*n`.

**Edge cases.** To measure the program outside the subject, we wrote 35 other requests with their expected answers, on 14 functions: the four types, up to three parameters, empty strings, large numbers, special characters and similar names (`fn_greet` and `fn_greet_formal`). The files of this measure are not in the repository.

| Version | Correct function | Exact call |
|---|---|---|
| First version | 31/35 (89 %) | 23/35 (66 %) |
| A token starting with `"` can end a function name | 32/35 (91 %) | 24/35 (69 %) |
| Leading zeros accepted | 32/35 (91 %) | 25/35 (71 %) |
| Chat format (current version) | **34/35 (97 %)** | **28/35 (80 %)** |

On 10 of these requests, adding one instruction sentence to the prompt lowered the correct functions from 6 to 4, and broke the regex `[0-9]+` of the subject.

**Speed.** The time is spent in the model: one call takes 1.1 to 3.8 s for 138 tokens, and 0.6 to 1.3 s for 36 tokens. Building the mask takes about 0.1 to 0.2 s. The total changes a lot between runs.

**Optimization.** The choice of the function stops as soon as only one name is still possible. On the 11 prompts this takes 24 model calls instead of 55, with the same names.

**Known limits.** The 7 remaining errors of the 35 requests:
- `"` and `\` cannot be generated inside a string: `'He said "hi"'` gives `'hi'`.
- The model sometimes copies the quotes of an empty string: `Repeat '' 5 times` gives `''`.
- Regex meaning: "replace every digit" gave `digit`, "replace every space" gave ` / /`.
- Some requests are misread: "Greet the user named O'Brien" chooses `fn_greet_formal`, "Greet Dr. Smith formally" gives the title `Dr. Smith`, "square root of 1e6" gives `10000`.
- A request that chooses a function with a parameter type other than `number`, `integer`, `string` or `boolean` fails and is left out of the output file.

## Challenges faced

| Problem | Cause | Solution |
|---|---|---|
| `-4.5` became `1200` | ` -` (space and minus) is one token; writing the space ourselves split it | no space after `:` |
| A string value looped until the limit (`cat.*cat.*...`) | the model wanted to finish with `",`, a single token that was forbidden | any token starting with `"` ends a string |
| A number value could loop (`1000000...`) | same problem with `}` followed by a line break | any token starting with `,` or `}` ends a number |
| Wrong regex (`34` for "all numbers") | text with a space after `:` | without the space the model gives `[0-9]+` |
| Crash on `"\ud800"` in a prompt | valid JSON, but impossible to encode in UTF-8 | refused when the file is read |
| Crash with an unknown model | the `OSError` of Hugging Face was not caught | turned into a clear error message |
| mypy reported nothing between our files | without `src/__init__.py`, the `src` imports were treated as `Any` | file added to the repository |
| "Say hello to Bob" chose `fn_greet_formal` | after `fn_greet`, the model wanted `",` (probability 0.71), but only `"` alone could end the name, so `_form` won | any token starting with `"` ends a complete name |
| "alarm at 18:05" gave `minute: 0` | the model hesitated between `0` and `5` (0.498 each) and took `0`; then it wanted `5`, but `05` is not valid JSON, so the only allowed token was the end | leading zeros accepted, then removed |
| `fn_greet_formal` chosen for "Greet alice", `hello` for an empty string | the raw text prompt; extra instructions made it worse | chat format of Qwen |

## Testing strategy

**Unit tests.** `make test` runs 72 pytest tests on the value rules, without the model, in less than a second. The cases come from the bugs of the project: `２`, `05`, `",`, `}\n\n`, `fn_greet"`. To check that the tests catch a bug, the removal of leading zeros was broken on purpose: 6 tests failed.

**Other checks**, done with short scripts and by running the program:

| Part | Check |
|---|---|
| Number and integer rules | every text of up to 5 characters made of `0 1 5 . - e +`: once the leading zeros are removed, `json.loads` gives the same value (1392 numbers, 483 integers) |
| Number beginnings | every beginning of a complete number is accepted, on the same texts |
| Boolean rules | 9 requests with the real model, all correct |
| String rule | every allowed token of the vocabulary is read back unchanged by `json.loads` |
| Token table | 5000 random tokens, no difference with `model.decode` |
| Input errors | missing file, invalid JSON, binary file, wrong types, duplicates, very deep JSON, byte order mark |
| Model errors | unknown model names (tested offline) |
| Failing requests | simulated errors: the next requests are still handled |
| Output file | keys and types compared with `functions_definition.json`, paths that cannot be written |
| Whole program | the 11 prompts of the subject, several times during development, with `make run` and no option |
| Edge cases | 35 requests with expected answers (see "Performance analysis") |
| Diagnosis | when an answer was wrong, the most likely tokens were printed at each step, with and without the mask |
| Style and types | flake8 without error; mypy with the flags of the subject and `--no-namespace-packages` (`llm_sdk` is excluded) |

## Resources

- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702), Willard and Louf, 2023
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) (GPT-2, byte level BPE)
- [RFC 8259: the JSON format](https://www.rfc-editor.org/rfc/rfc8259)
- Python documentation: [re](https://docs.python.org/3/library/re.html), [json](https://docs.python.org/3/library/json.html), [argparse](https://docs.python.org/3/library/argparse.html)
- [pydantic documentation](https://docs.pydantic.dev/) and [NumPy documentation](https://numpy.org/doc/)

### AI usage

An AI assistant (Claude Code) was used mainly as a teacher, for the theory: function calling, tokenization, logits, constrained decoding, and the Python syntax needed. For each design choice it explained the options and their trade-offs, and the author decided.

