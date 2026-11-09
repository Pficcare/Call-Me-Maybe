import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from src.schemas import FunctionCall, FunctionDefinition, PromptRequest


def read_json(path: Path) -> object:  # Plus strict que Any : à valider
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except OSError as error:
        raise ValueError(f"Cannot read '{path}': {error}") from error
    except (ValueError, RecursionError) as error:
        raise ValueError(f"Invalid JSON in '{path}': {error}") from error


def load_functions(path: Path) -> list[FunctionDefinition]:
    data = read_json(path)
    adapter = TypeAdapter(list[FunctionDefinition])
    try:
        functions = adapter.validate_python(data)
    except ValidationError as error:
        raise ValueError(f"Invalid format in '{path}': {error}") from error

    if not functions:
        raise ValueError(f"No function defined in '{path}'")

    seen: set[str] = set()
    for el in functions:
        if el.name in seen:
            raise ValueError(
                f"Duplicate function name in '{path}': {el.name}"
            )
        seen.add(el.name)
    return functions


def load_prompt(path: Path) -> list[PromptRequest]:
    
    data = read_json(path)
    adapter = TypeAdapter(list[PromptRequest])
    try:
        return adapter.validate_python(data)
    except ValidationError as error:
        raise ValueError(f"Invalid format in '{path}': {error}") from error


def results(path: Path, calls: list[FunctionCall]) -> None:
    
    data = [call.model_dump() for call in calls]
    try:
        text = json.dumps(data, indent=4, allow_nan=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
    except (OSError, ValueError) as error:
        raise ValueError(f"Cannot write '{path}': {error}") from error
