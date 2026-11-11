from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def load_model(model_name: str) -> "Small_LLM_Model": # Reference differer Mpy/Python
    from llm_sdk import Small_LLM_Model
    
    try:
        model = Small_LLM_Model(model_name)
    except Exception as e:
        raise e
    return model




def encode_text(model: "Small_LLM_Model", text: str) -> list[int]:
    ids: list[int] = model.encode(text)[0].tolist()
    return ids


def get_next_logits(model: "Small_LLM_Model", ids: list[int]) -> npt.NDArray[np.float64]:
    logits = model.get_logits_from_input_ids(ids)
    return np.array(logits, dtype=np.float64)
