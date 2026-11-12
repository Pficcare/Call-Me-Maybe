from typing import TYPE_CHECKING

from src.llm import encode_text
from src.schemas import PromptRequest, FunctionDefinition
from src.prompts import build_selection_prompt
from src.decoder import generate_choice

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def explore_prompts(model: "Small_LLM_Model",vocab: dict[int, str],prompts: list[PromptRequest], functions: list[FunctionDefinition]) -> None:
    for prompt in prompts:
        print(f"\nPrompt: {prompt.prompt!r}") #!r ca donne ""
        function = select_function(prompt, functions, model, vocab)
        print(f"  -> {function.name}")


def select_function(request: PromptRequest, functions: list[FunctionDefinition],model: "Small_LLM_Model", vocab: dict[int,str]) -> FunctionDefinition:
    
    prompt = build_selection_prompt(request, functions)
    
    ids = encode_text(model, prompt)
    
    names :list[str] = []
    for el in functions:
        names.append(el.name)

    selcted_name = generate_choice(model, vocab, ids, names)
    
    for function in functions:
        if function.name == selcted_name:
            return function
    
    raise RuntimeError

    
