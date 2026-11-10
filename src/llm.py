from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


def load_model(model_name: str) -> "Small_LLM_Model": # Reference differer Mpy/Python
    from llm_sdk import Small_LLM_Model
    
    try:
        model = Small_LLM_Model(model_name)
    except Exception as e:
        raise e
    return model




# def encode_text(model: "Small_LLM_Model", text: str) -> list[int]:
    



