import sys

from src.arguments import parser_args
from src.generator import process_prompts
from src.json_io import check_output, load_functions, load_prompt, results
from src.llm import get_vocab_path, load_model
from src.tokens import load_vocabulary


def main() -> int:
    try:
        args = parser_args()
        functions = load_functions(args.functions_definition)
        print(f"{len(functions)} functions loaded")
        prompts = load_prompt(args.input)
        print(f"{len(prompts)} prompts loaded")
        check_output(args.output)
        model = load_model(args.model)
        print(f"Model {args.model} loaded")
        vocab = load_vocabulary(get_vocab_path(model))
        print(f"{len(vocab)} tokens in vocabulary table")
        calls = process_prompts(model, vocab, prompts, functions)
        results(args.output, calls)
        print(f"\n{len(calls)} function calls written to {args.output}")
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130 #Shell code erreur pour ce type d Interupt
    return 0


if __name__ == "__main__":
    sys.exit(main()) #retourn le bon code d erreur au shell
