from typing import TYPE_CHECKING

from src.display import show_top_tokens
from src.llm import encode_text, get_next_logits
from src.schemas import PromptRequest

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def explore_prompts(model: "Small_LLM_Model",vocab: dict[int, str],prompts: list[PromptRequest]) -> None:
    for prompt in prompts:
        print(f"\nPrompt: {prompt.prompt!r}") #!r ca donne ""
        ids = encode_text(model, prompt.prompt)
        logits = get_next_logits(model, ids)
        show_top_tokens(logits, vocab, 5)
