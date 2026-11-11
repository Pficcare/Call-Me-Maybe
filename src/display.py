import numpy as np
import numpy.typing as npt


def show_top_tokens(
    logits: npt.NDArray[np.float64], vocab: dict[int, str], count: int
) -> None:
    best_ids = np.argsort(-logits)[:count]
    for token_id in best_ids:
        text = vocab.get(int(token_id), "<special>")
        print(f"  {token_id:>6} {text!r:<15} logit={logits[token_id]:6.2f}")
