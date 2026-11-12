import sys

from src.arguments import parser_args
from src.generator import explore_prompts
from src.json_io import load_functions, load_prompt
from src.llm import load_model
from src.tokens import load_vocabulary


def main() -> int:
    try:
        args = parser_args()
        functions = load_functions(args.functions_definition)
        print(f"{len(functions)} functions loaded")
        prompts = load_prompt(args.input)
        print(f"{len(prompts)} prompts loaded")
        model = load_model(args.model)
        print(f"Model {args.model} loaded")
        vocab = load_vocabulary(model.get_path_to_vocab_file())
        print(f"{len(vocab)} tokens in vocabulary table")
        explore_prompts(model, vocab, prompts, functions)
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130 #Shell code erreur pour ce type d Interupt
    return 0


if __name__ == "__main__":
    sys.exit(main()) #retourn le bon code d erreur au shell
