"""Command line interface."""

import argparse
from pathlib import Path
from collections.abc import Sequence

def parser_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    
    funct_def: str = "data/input/functions_definition.json"
    input_path: str = "data/input/function_calling_tests.json"
    output_path:str = "data/output/function_calling_results.json"
    model_name:str = "Qwen/Qwen3-0.6B"


    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition", type=Path, default=Path(funct_def))
    parser.add_argument("--input", type=Path, default=Path(input_path))
    parser.add_argument("--output", type=Path, default=Path(output_path))
    parser.add_argument("--model", type=str, default=model_name)
    
    return parser.parse_args(argv)

