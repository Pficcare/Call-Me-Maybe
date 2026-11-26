import json
from collections.abc import Callable

import pytest

from src.rules import (
    is_boolean_prefix,
    is_choice_prefix,
    is_integer_complete,
    is_integer_prefix,
    is_number_complete,
    is_number_prefix,
    is_string_prefix,
    is_value_complete,
    is_value_end,
    is_value_prefix,
    remove_leading_zeros,
)


@pytest.mark.parametrize("text", ["0", "-4.5", "2.0", "1e6", "1E-3", "05", "007.5"])
def test_number_complete_accepts(text: str) -> None:
    assert is_number_complete(text)


@pytest.mark.parametrize("text", ["", "-", "1.", "1e", ".5", "+1", "1.2.3", "NaN", "２"])
def test_number_complete_refuses(text: str) -> None:
    assert not is_number_complete(text)


@pytest.mark.parametrize("text", ["", "-", "1.", "1e", "1e-", "12.5"])
def test_number_prefix_accepts(text: str) -> None:
    assert is_number_prefix(text)


@pytest.mark.parametrize("text", [".", "1..", "1e1.5", "-x", " 1"])
def test_number_prefix_refuses(text: str) -> None:
    assert not is_number_prefix(text)


@pytest.mark.parametrize("text", ["0", "42", "-7", "05"])
def test_integer_complete_accepts(text: str) -> None:
    assert is_integer_complete(text)


@pytest.mark.parametrize("text", ["", "-", "1.0", "1e3", "4.5"])
def test_integer_complete_refuses(text: str) -> None:
    assert not is_integer_complete(text)


def test_integer_prefix() -> None:
    assert is_integer_prefix("-")
    assert not is_integer_prefix("1.")


@pytest.mark.parametrize(
    "text, expected",
    [("05", "5"), ("-007", "-7"), ("0", "0"), ("0.5", "0.5"),
     ("00.5", "0.5"), ("1e05", "1e05"), ("100", "100"), ("000", "0")],
)
def test_remove_leading_zeros(text: str, expected: str) -> None:
    assert remove_leading_zeros(text) == expected


@pytest.mark.parametrize("text", ["05", "-007", "00.5", "1e05", "0"])
def test_remove_leading_zeros_gives_valid_json(text: str) -> None:
    assert json.loads(remove_leading_zeros(text)) == float(text)


def test_boolean_prefix() -> None:
    assert is_boolean_prefix("")
    assert is_boolean_prefix("tr")
    assert is_boolean_prefix("false")
    assert not is_boolean_prefix("True")
    assert not is_boolean_prefix("truex")


@pytest.mark.parametrize("text", ["", "hello", "O'Brien", "[0-9]+", "é ü 字"])
def test_string_prefix_accepts(text: str) -> None:
    assert is_string_prefix(text)


@pytest.mark.parametrize("text", ['say "hi"', "back\\slash", "line\nbreak", "tab\t"])
def test_string_prefix_refuses(text: str) -> None:
    assert not is_string_prefix(text)


def test_choice_prefix() -> None:
    names = ["fn_greet", "fn_greet_formal"]
    assert is_choice_prefix("", names)
    assert is_choice_prefix("fn_greet", names)
    assert is_choice_prefix("fn_greet_f", names)
    assert not is_choice_prefix("fn_greet_x", names)
    assert not is_choice_prefix('fn_greet"', names)


@pytest.mark.parametrize("token", [",", ",\n", "}", "}\n\n"])
def test_value_end_for_numbers(token: str) -> None:
    assert is_value_end(token, "number")
    assert is_value_end(token, "integer")
    assert is_value_end(token, "boolean")
    assert not is_value_end(token, "string")


@pytest.mark.parametrize("token", ['"', '",', '"}\n'])
def test_value_end_for_strings(token: str) -> None:
    assert is_value_end(token, "string")
    assert not is_value_end(token, "number")


def test_value_rules_follow_the_type() -> None:
    assert is_value_complete("12", "integer")
    assert not is_value_complete("1.5", "integer")
    assert is_value_complete("1.5", "number")
    assert is_value_complete("true", "boolean")
    assert is_value_complete("", "string")
    assert is_value_prefix("fa", "boolean")


@pytest.mark.parametrize("rule", [is_value_prefix, is_value_complete, is_value_end])
def test_unknown_type_is_refused(rule: Callable[[str, str], bool]) -> None:
    with pytest.raises(ValueError, match="Unsupported parameter type"):
        rule("1", "array")
