from pathlib import Path
from src.json_io import read_json
from pydantic import TypeAdapter, ValidationError



def byte_decoder() -> dict[str, int]:
    
    print_b: set[int] = set(range(33,127)) | set(range(161, 173)) | set(range(174, 256))
    decoder: dict[str,int] = {}

    for el in print_b:
        decoder[chr(el)] = el

    i = 0
    for el in range(256):
        if el not in print_b:
            decoder[chr(256 + i)] = el
            i += 1

    return decoder


def decode_token(token: str, byte_decoder: dict[str, int]) -> str | None:
    
    l_octet: list[int] = []

    for c in token:
        x = byte_decoder[c]
        l_octet.append(x)
    try:
        text = bytes(l_octet).decode("utf-8")
    except UnicodeDecodeError:
        return None
    return text



def load_vocabulary(path: str) -> dict[int, str]:
    
    p = Path(path) 

    jason = read_json(p)

    adapter = TypeAdapter(dict[str,int])
    try:
        datas: dict[str,int]= adapter.validate_python(jason)
    except ValidationError as e:
        raise ValueError

    decoder: dict[str, int] = byte_decoder()

    vocab: dict[int, str] = {}
    
    for el, id in datas.items():
        txt = decode_token(el, decoder)
        if txt is None:
            continue
        vocab[id] = txt
    return vocab




