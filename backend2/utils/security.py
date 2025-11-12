from typing import Optional


def hash_password(password: str) -> str:
    # placeholder: do not use in production
    return "hashed-" + password


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
def hash_password(pw: str) -> str:
    # placeholder
    return pw
