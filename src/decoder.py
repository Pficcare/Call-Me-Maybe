from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from src.llm import get_next_logits
from src.rules import is_choice_prefix

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
    for token_id, text in vocab.items():
        if text and is_choice_prefix(current + text, choices):
            allowed.append(token_id)
    return allowed


def generate_choice(
    model: "Small_LLM_Model",
    vocab: dict[int, str],
    ids: list[int],
    choices: list[str],
) -> str:
    targets: list[str] = []
    for choice in choices:
        targets.append(choice + '"')
    current = ""
    while not current.endswith('"'):
        logits = get_next_logits(model, ids)
        allowed = find_choice_tokens(current, vocab, targets)
        token_id = select_token(apply_mask(logits, allowed))
        ids.append(token_id)
        current += vocab[token_id]
    return current[:-1]
