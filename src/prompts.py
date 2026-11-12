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


def build_selection_prompt(request: PromptRequest,functions: list[FunctionDefinition],) -> str:
    
    catalog = format_function(functions)
    
    return (
        "Available functions:\n"
        f"{catalog}\n\n"
        f"Request: {request.prompt}\n"
        'Function call: {"name": "'
    )
