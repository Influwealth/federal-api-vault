def extract_opportunities(data: dict) -> list[dict]:
    """Extracts normalized opportunity list."""
    ops = data.get("opportunities") or data.get("results") or []
    return [{
        "title": item.get("title"),
        "agency": item.get("agency") or item.get("department"),
        "posted": item.get("postedDate") or item.get("posted"),
        "close": item.get("closeDate") or item.get("close"),
        "url": item.get("url") or item.get("link"),
    } for item in ops]
