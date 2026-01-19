def validate_ein(ein: str) -> bool:
    """Basic EIN validator: 9 digits, optional dash."""
    ein = (ein or "").replace("-", "").strip()
    return len(ein) == 9 and ein.isdigit()
