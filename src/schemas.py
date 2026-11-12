
from typing import Literal

from pydantic import BaseModel, ConfigDict

ArgumentValue = float | int | str | bool


class ParameterSpec(BaseModel):
    """Type of one function parameter."""

    type: Literal["number", "integer", "string", "boolean"]


class ReturnSpec(BaseModel):
    """Return type of a function. It has no effect on the generation."""

    type: str


class FunctionDefinition(BaseModel):
    """One callable function, as described in functions_definition.json."""

    name: str
    description: str
    parameters: dict[str, ParameterSpec]
    returns: ReturnSpec


class PromptRequest(BaseModel):
    """One natural language request, from function_calling_tests.json."""

    prompt: str


class FunctionCall(BaseModel):
    """One entry of the output file. Extra keys are forbidden."""

    model_config = ConfigDict(extra="forbid")

    prompt: str
    name: str
    parameters: dict[str, ArgumentValue]
