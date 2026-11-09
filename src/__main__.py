
import sys

from src.arguments import parser_args


def main() -> int:
    try:
        args = parser_args()
        print(f"functions_definition: {args.functions_definition}")
        print(f"input: {args.input}")
        print(f"output: {args.output}")
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130 #Shell code erreur pour ce type d Interupt
    return 0


if __name__ == "__main__":
    sys.exit(main()) #retourn le bon code d erreur au shell
