def wotc_eligibility(applicant: dict) -> dict:
    """Placeholder WOTC eligibility logic."""
    age = int(applicant.get("age", 0) or 0)
    return {"name": applicant.get("name"), "eligible": age < 40}
