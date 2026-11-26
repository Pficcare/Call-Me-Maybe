from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from src.llm import get_next_logits
from src.rules import is_choice_prefix, is_value_complete, is_value_end, is_value_prefix

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def apply_mask(logits: npt.NDArray[np.float64], allowed_ids: list[int],) -> npt.NDArray[np.float64]:
    
    masked = np.full_like(logits, -np.inf)
    masked[allowed_ids] = logits[allowed_ids]
    return masked


def select_token(masked_logits: npt.NDArray[np.float64]) -> int:
    
    if np.isneginf(masked_logits).all():
        raise RuntimeError("No allowed token")
    return int(np.argmax(masked_logits))


def find_choice_tokens(
    current: str, vocab: dict[int, str], choices: list[str]
) -> list[int]:
    allowed: list[int] = []
    can_stop = current in choices
    for token_id, text in vocab.items():
        if is_value_end(text, "string"):
            if can_stop:
                allowed.append(token_id)
        elif text and is_choice_prefix(current + text, choices):
            allowed.append(token_id)
    return allowed


def find_matching_choices(current: str, choices: list[str]) -> list[str]:
    matching: list[str] = []
    for choice in choices:
        if choice.startswith(current):
            matching.append(choice)
    return matching


def generate_choice(
    model: "Small_LLM_Model",
    vocab: dict[int, str],
    ids: list[int],
    choices: list[str],
) -> str:
    current = ""
    remaining = choices
    while len(remaining) > 1:
        logits = get_next_logits(model, ids)
        allowed = find_choice_tokens(current, vocab, remaining)
        token_id = select_token(apply_mask(logits, allowed))
        if is_value_end(vocab[token_id], "string"):
            return current
        ids.append(token_id)
        current += vocab[token_id]
        remaining = find_matching_choices(current, remaining)
    return remaining[0]


def find_value_tokens(
    current: str, vocab: dict[int, str], param_type: str
) -> list[int]:
    allowed: list[int] = []
    can_stop = is_value_complete(current, param_type)
    for token_id, text in vocab.items():
        if is_value_end(text, param_type):
            if can_stop:
                allowed.append(token_id)
        elif text and is_value_prefix(current + text, param_type):
            allowed.append(token_id)
    return allowed


def generate_value(
    model: "Small_LLM_Model",
    vocab: dict[int, str],
    ids: list[int],
    param_type: str,
) -> str:
    max_tokens = 100
    current = ""
    for _ in range(max_tokens):
        logits = get_next_logits(model, ids)
        allowed = find_value_tokens(current, vocab, param_type)
        token_id = select_token(apply_mask(logits, allowed))
        if is_value_end(vocab[token_id], param_type):
            return current
        ids.append(token_id)
        current += vocab[token_id]
    raise RuntimeError(f"Value not finished after {max_tokens} tokens: {current[:20]}...")
