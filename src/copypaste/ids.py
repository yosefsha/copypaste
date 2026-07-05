import secrets

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_ID_LENGTH = 7


def generate_id() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(_ID_LENGTH))
