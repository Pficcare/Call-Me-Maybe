from collections.abc import Sequence


def is_choice_prefix(text: str, choices: Sequence[str]) -> bool:
    for choice in choices:
        if choice.startswith(text):
            return True
    return False
