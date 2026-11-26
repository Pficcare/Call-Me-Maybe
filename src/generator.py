import json
import math
import sys
from typing import TYPE_CHECKING

from src.llm import encode_text
from src.schemas import ArgumentValue, FunctionCall, FunctionDefinition, PromptRequest
from src.prompts import build_arguments_prompt, build_selection_prompt
from src.decoder import generate_choice, generate_value
from src.rules import remove_leading_zeros

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def explore_prompts(model: "Small_LLM_Model",vocab: dict[int, str],prompts: list[PromptRequest], functions: list[FunctionDefinition]) -> list[FunctionCall]:

    calls: list[FunctionCall] = []

    for prompt in prompts:
        print(f"\nPrompt: {prompt.prompt!r}") #!r ca donne ""
        try:
            function = select_function(prompt, functions, model, vocab)
            print(f"  -> {function.name}")
            arguments = extract_arguments(prompt, function, model, vocab)
            call = build_call(prompt, function, arguments)
            print(f"  -> {call.parameters}")
            calls.append(call)
        except (ValueError, RuntimeError) as error:
            print(f"  -> Error: {error}", file=sys.stderr)

    failed = len(prompts) - len(calls)
    if failed > 0:
        print(f"{failed} of {len(prompts)} prompts failed", file=sys.stderr)

    return calls


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
    
    raise RuntimeError(f"Unknown function: {selcted_name}")


def extract_arguments(request: PromptRequest, function: FunctionDefinition, model: "Small_LLM_Model", vocab: dict[int, str]) -> str:

    if not function.parameters:
        return "{}"

    prompt = build_arguments_prompt(request, function)
    arguments = ""
    remaining = len(function.parameters)

    for name, spec in function.parameters.items():
        remaining -= 1
        if remaining == 0:
            terminator = "}"
        else:
            terminator = ","

        quote = ""
        if spec.type == "string":
            quote = '"'

        arguments += json.dumps(name) + ":" + quote
        ids = encode_text(model, prompt + arguments)
        value = generate_value(model, vocab, ids, spec.type)
        if spec.type in ("number", "integer"):
            value = remove_leading_zeros(value)
        arguments += value + quote + terminator

    return "{" + arguments


def build_call(request: PromptRequest, function: FunctionDefinition, arguments: str) -> FunctionCall:

    parameters: dict[str, ArgumentValue] = json.loads(arguments)

    for name, spec in function.parameters.items():
        if spec.type == "number":
            try:
                number = float(parameters[name])
            except OverflowError as error:
                raise ValueError(f"Number too large for '{name}'") from error
            if not math.isfinite(number):
                raise ValueError(f"Number too large for '{name}'")
            parameters[name] = number

    return FunctionCall(prompt=request.prompt, name=function.name, parameters=parameters)
