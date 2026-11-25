from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def load_model(model_name: str) -> "Small_LLM_Model": # Reference differer Mpy/Python
    from llm_sdk import Small_LLM_Model
    
    try:
        model = Small_LLM_Model(model_name)
    except OSError as error:
        raise ValueError(f"Cannot load model '{model_name}': {error}") from error
    return model


def get_vocab_path(model: "Small_LLM_Model") -> str:
    try:
        path: str = model.get_path_to_vocab_file()
    except OSError as error:
        raise ValueError(f"Cannot find the vocabulary file: {error}") from error
    return path


def encode_text(model: "Small_LLM_Model", text: str) -> list[int]:
    ids: list[int] = model.encode(text)[0].tolist()
    return ids


def get_next_logits(model: "Small_LLM_Model", ids: list[int]) -> npt.NDArray[np.float64]:
    logits = model.get_logits_from_input_ids(ids)
    return np.array(logits, dtype=np.float64)
