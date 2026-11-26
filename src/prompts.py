from src.schemas import FunctionDefinition, PromptRequest


def format_function(functions: list[FunctionDefinition]) -> str:
    lines: list[str] = []

    for function in functions:
        params: list[str] = []
        for name, spec in function.parameters.items():
            params.append(f"{name}: {spec.type}")
        signature = f"{function.name}({', '.join(params)})"
        lines.append(f"- {signature}: {function.description}")

    return "\n".join(lines)


def build_chat_prompt(user: str, answer_start: str) -> str:
    return (
        f"<|im_start|>user\n{user}<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think>\n\n</think>\n\n"
        f"{answer_start}"
    )


def build_selection_prompt(
    request: PromptRequest, functions: list[FunctionDefinition]
) -> str:

    catalog = format_function(functions)

    user = (
        "Available functions:\n"
        f"{catalog}\n\n"
        f"Request: {request.prompt}\n"
        "Answer with the function call in JSON."
    )
    return build_chat_prompt(user, '{"name": "')


def build_arguments_prompt(
    request: PromptRequest, function: FunctionDefinition
) -> str:

    signature = format_function([function])

    user = (
        "Function:\n"
        f"{signature}\n\n"
        f"Request: {request.prompt}\n"
        "Answer with the arguments in JSON."
    )
    return build_chat_prompt(user, "{")
