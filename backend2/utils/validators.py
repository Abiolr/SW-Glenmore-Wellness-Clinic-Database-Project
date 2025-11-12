def is_valid_phone(phone: str) -> bool:
    return phone is not None and len(phone) >= 7
def validate_email(email: str) -> bool:
    return "@" in email
