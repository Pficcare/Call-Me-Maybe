import re
from collections.abc import Sequence


def is_choice_prefix(text: str, choices: Sequence[str]) -> bool:
    for choice in choices:
        if choice.startswith(text):
            return True
    return False


def is_number_complete(text: str) -> bool:
    pattern = r"-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?"
    return re.fullmatch(pattern, text) is not None


def is_number_prefix(text: str) -> bool:
    return is_number_complete(text) or is_number_complete(text + "0")


def is_value_prefix(text: str, param_type: str) -> bool:
    if param_type == "number":
        return is_number_prefix(text)
    raise ValueError(f"Unsupported parameter type: {param_type}")


def is_value_complete(text: str, param_type: str) -> bool:
    if param_type == "number":
        return is_number_complete(text)
    raise ValueError(f"Unsupported parameter type: {param_type}")
