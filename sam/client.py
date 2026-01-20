"""
SAM.gov Entity API client with real implementation.
Docs: https://open.gsa.gov/api/entity-api/
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.http_client import SAMClient
from typing import Optional, Dict, Any, List


class SAMEntityAPI:
    """SAM.gov Entity Management Data API wrapper."""
    
    def __init__(self):
        self.client = SAMClient()
    
    def get_entity_by_uei(self, uei: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity details by Unique Entity ID (UEI)."""
        try:
            params = {
                "ueiSAM": uei.strip().upper(),
                "includeSections": "entityRegistration,coreData,assertions"
            }
            response = self.client.get("", params=params)
            
            if response.get("totalRecords", 0) > 0:
                return response.get("entityData", [{}])[0]
            return None
        
        except Exception as e:
            print(f"Error fetching UEI {uei}: {e}")
            return None
    
    def get_entity_by_cage(self, cage_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity by CAGE code."""
        try:
            params = {
                "cageCode": cage_code.strip().upper(),
                "includeSections": "entityRegistration,coreData"
            }
            response = self.client.get("", params=params)
            
            if response.get("totalRecords", 0) > 0:
                return response.get("entityData", [{}])[0]
            return None
        
        except Exception as e:
            print(f"Error fetching CAGE {cage_code}: {e}")
            return None
    
    def search_by_name(self, legal_business_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities by legal business name."""
        try:
            params = {
                "legalBusinessName": legal_business_name.strip(),
                "includeSections": "entityRegistration",
                "page": "0",
                "size": str(limit)
            }
            response = self.client.get("", params=params)
            return response.get("entityData", [])
        
        except Exception as e:
            print(f"Error searching for '{legal_business_name}': {e}")
            return []
    
    def get_exclusions(self, uei: str) -> List[Dict[str, Any]]:
        """Check if entity has any active exclusions."""
        try:
            params = {
                "ueiSAM": uei.strip().upper(),
                "includeSections": "exclusionDetails"
            }
            response = self.client.get("", params=params)
            
            if response.get("totalRecords", 0) > 0:
                entity = response.get("entityData", [{}])[0]
                return entity.get("exclusionDetails", {}).get("exclusions", [])
            return []
        
        except Exception as e:
            print(f"Error checking exclusions for {uei}: {e}")
            return []
    
    def validate_entity_status(self, uei: str) -> Dict[str, Any]:
        """Comprehensive entity status validation."""
        entity = self.get_entity_by_uei(uei)
        exclusions = self.get_exclusions(uei)
        
        if not entity:
            return {
                "uei": uei,
                "error": "Entity not found",
                "is_active": False
            }
        
        core = entity.get("coreData", {})
        reg = entity.get("entityRegistration", {})
        
        return {
            "uei": uei,
            "cage": core.get("cageCode"),
            "legal_name": core.get("legalBusinessName"),
            "dba_name": core.get("dbaName"),
            "registration_status": reg.get("registrationStatus"),
            "registration_date": reg.get("registrationDate"),
            "expiration_date": reg.get("expirationDate"),
            "is_active": reg.get("registrationStatus") == "Active",
            "has_exclusions": len(exclusions) > 0,
            "exclusion_count": len(exclusions),
            "physical_address": core.get("physicalAddress", {}),
            "entity_structure": core.get("entityStructureCode")
        }


def parse_entity_status(api_response: dict) -> dict:
    """Legacy compatibility - normalizes SAM.gov entity response."""
    core = api_response.get("coreData", {})
    reg = api_response.get("entityRegistration", {})
    
    return {
        "uei": core.get("ueiSAM"),
        "cage": core.get("cageCode"),
        "status": reg.get("registrationStatus"),
        "expiration": reg.get("expirationDate"),
        "legal_name": core.get("legalBusinessName")
    }


def generate_sam_payload(business: dict) -> dict:
    """Generate SAM.gov registration payload structure."""
    return {
        "entity": {
            "legalBusinessName": business.get("legal_name"),
            "dbaName": business.get("dba"),
            "taxIdentifier": business.get("ein"),
            "physicalAddress": {
                "addressLine1": business.get("address", {}).get("line1"),
                "city": business.get("address", {}).get("city"),
                "stateOrProvinceCode": business.get("address", {}).get("state"),
                "zipCode": business.get("address", {}).get("zip"),
                "countryCode": business.get("address", {}).get("country", "USA")
            },
            "naicsCodes": business.get("naics", []),
            "businessTypes": business.get("business_types", [])
        }
    }
