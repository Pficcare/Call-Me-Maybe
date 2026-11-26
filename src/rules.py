import re
from collections.abc import Sequence


def is_choice_prefix(text: str, choices: Sequence[str]) -> bool:
    for choice in choices:
        if choice.startswith(text):
            return True
    return False


def is_number_complete(text: str) -> bool:
    pattern = r"-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?"
    return re.fullmatch(pattern, text) is not None


def is_number_prefix(text: str) -> bool:
    return is_number_complete(text) or is_number_complete(text + "0")


def is_integer_complete(text: str) -> bool:
    pattern = r"-?[0-9]+"
    return re.fullmatch(pattern, text) is not None


def is_integer_prefix(text: str) -> bool:
    return is_integer_complete(text) or is_integer_complete(text + "0")


def remove_leading_zeros(text: str) -> str:
    return re.sub(r"^(-?)0+(?=[0-9])", r"\1", text)


def is_boolean_complete(text: str) -> bool:
    return text == "true" or text == "false"


def is_boolean_prefix(text: str) -> bool:
    return "true".startswith(text) or "false".startswith(text)


def is_string_prefix(text: str) -> bool:
    pattern = r'[^"\\\x00-\x1f]*'
    return re.fullmatch(pattern, text) is not None


def is_value_prefix(text: str, param_type: str) -> bool:
    if param_type == "number":
        return is_number_prefix(text)
    if param_type == "integer":
        return is_integer_prefix(text)
    if param_type == "boolean":
        return is_boolean_prefix(text)
    if param_type == "string":
        return is_string_prefix(text)
    raise ValueError(f"Unsupported parameter type: {param_type}")


def is_value_complete(text: str, param_type: str) -> bool:
    if param_type == "number":
        return is_number_complete(text)
    if param_type == "integer":
        return is_integer_complete(text)
    if param_type == "boolean":
        return is_boolean_complete(text)
    if param_type == "string":
        return is_string_prefix(text)
    raise ValueError(f"Unsupported parameter type: {param_type}")


def is_value_end(text: str, param_type: str) -> bool:
    if param_type in ("number", "integer", "boolean"):
        return text.startswith(",") or text.startswith("}")
    if param_type == "string":
        return text.startswith('"')
    raise ValueError(f"Unsupported parameter type: {param_type}")
