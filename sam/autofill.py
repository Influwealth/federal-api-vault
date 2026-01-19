def generate_sam_payload(business: dict) -> dict:
    """
    Starter SAM.gov registration payload shape.
    business = {"legal_name": "", "dba": "", "ein": "", "address": "", "naics": []}
    """
    return {
        "entity": {
            "legalBusinessName": business.get("legal_name"),
            "dbaName": business.get("dba"),
            "taxIdentifier": business.get("ein"),
            "address": business.get("address"),
            "naicsCodes": business.get("naics", []),
        }
    }
