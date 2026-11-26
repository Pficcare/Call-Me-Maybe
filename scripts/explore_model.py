import json
import time

import numpy as np
from llm_sdk import Small_LLM_Model


def load_model() -> Small_LLM_Model:
    print("Loading the model (downloaded on the first run)...")
    start = time.time()
    model = Small_LLM_Model()
    print(f"Model loaded in {time.time() - start:.1f} s\n")
    return model


def show_tokens(model: Small_LLM_Model, text: str) -> None:
    ids = model.encode(text)[0].tolist() 
    print(f"Text: {text!r}")
    print(f"{len(ids)} tokens:")
    for token_id in ids:
        print(f"  {token_id:>6} -> {model.decode([token_id])!r}")
    print()


def show_top_tokens(model: Small_LLM_Model, text: str, count: int) -> None:
    ids = model.encode(text)[0].tolist() #Tensor 2d [1, n] On recup idx 0
    logits = np.array(model.get_logits_from_input_ids(ids))
    probas = np.exp(logits - logits.max())
    probas = probas / probas.sum()
    print(f"Text: {text!r}")
    print(f"Number of logits: {len(logits)}")
    print(f"Top {count} next tokens:")
    for token_id in np.argsort(-logits)[:count]:
        token = model.decode([int(token_id)])
        print(
            f"  {token_id:>6} {token!r:<12} "
            f"logit={logits[token_id]:6.2f}  proba={probas[token_id]:.1%}"
        )
    print()


def show_vocab(model: Small_LLM_Model, text: str) -> None:
    path = model.get_path_to_vocab_file()
    with open(path, encoding="utf-8") as file:
        vocab = json.load(file)
    id_to_token = {}
    for token, token_id in vocab.items():
        id_to_token[token_id] = token
    print(f"vocab.json: {path}")
    print(f"{len(vocab)} entries (token text -> id)")
    print(f"Raw vocab text vs decoded text for {text!r}:")
    for token_id in model.encode(text)[0].tolist():
        raw = id_to_token.get(token_id)
        print(f"  {token_id:>6} raw={raw!r:<10} decoded={model.decode([token_id])!r}")
    print()


def generate_greedy_boy(model: Small_LLM_Model, text: str, max_tokens: int) -> None:
    ids = model.encode(text)[0].tolist()
    print(f"Text: {text!r}")
    print("Generated: ", end="")
    start = time.time()
    for _ in range(max_tokens):
        logits = model.get_logits_from_input_ids(ids)
        next_id = int(np.argmax(logits))
        ids.append(next_id)
        print(repr(model.decode([next_id])), end=" ", flush=True)
    print(f"\n{max_tokens} tokens in {time.time() - start:.1f} s\n")


def main() -> None:
    model = load_model()

    print("=== 1. Tokenization ===")
    show_tokens(model, '{"name": "fn_add_numbers", "parameters": {"a": 265.0}}')

    print("=== 2. Logits of the next token ===")
    show_top_tokens(model, "What is the sum of 2 and 3? The answer is", 5)

    print("=== 3. The vocabulary file ===")
    show_vocab(model, 'Greet "shrek" now')

    print("=== 4. Greedy generation loop ===")
    generate_greedy_boy(model, "What is the sum of 2 and 3? The answer is", 10)


if __name__ == "__main__":
    main()
