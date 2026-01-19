def parse_entity_status(api_response: dict) -> dict:
    """Normalizes a SAM.gov entity response."""
    return {
        "uei": api_response.get("uei"),
        "cage": api_response.get("cage"),
        "status": api_response.get("status"),
        "expiration": api_response.get("expirationDate") or api_response.get("expiration"),
    }
