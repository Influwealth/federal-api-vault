"""
SBA API client for contracting opportunities and certifications.
Primary source: SAM.gov Contract Opportunities (beta.sam.gov)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typing import List, Dict, Any
import requests
from config import Config


class SBAOpportunitiesAPI:
    """SBA contracting opportunities via SAM.gov."""
    
    def __init__(self):
        self.base_url = "https://api.sam.gov/opportunities/v2/search"
        self.api_key = Config.SAM_API_KEY
    
    def search_opportunities(self,
                            keywords: str = "",
                            naics_code: str = "",
                            set_aside: str = "",
                            posted_from: str = "",
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Search federal contracting opportunities."""
        try:
            params = {
                "api_key": self.api_key,
                "ptype": "o",
                "limit": limit
            }
            
            if keywords:
                params["q"] = keywords
            if naics_code:
                params["ncode"] = naics_code
            if set_aside:
                params["typeOfSetAside"] = set_aside
            if posted_from:
                params["postedFrom"] = posted_from
            
            response = requests.get(
                self.base_url,
                params=params,
                headers={"X-Api-Key": self.api_key},
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("opportunitiesData", [])
        
        except Exception as e:
            print(f"Error searching opportunities: {e}")
            return []
    
    def get_8a_opportunities(self, naics_code: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Get opportunities set aside for 8(a) certified businesses."""
        return self.search_opportunities(set_aside="8A", naics_code=naics_code, limit=limit)
    
    def get_wosb_opportunities(self, naics_code: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Get opportunities for Women-Owned Small Businesses."""
        return self.search_opportunities(set_aside="WOSB", naics_code=naics_code, limit=limit)
    
    def get_hubzone_opportunities(self, naics_code: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Get HUBZone set-aside opportunities."""
        return self.search_opportunities(set_aside="HUBZone", naics_code=naics_code, limit=limit)


def extract_opportunities(data: dict) -> list[dict]:
    """Normalize opportunity data from SAM.gov or legacy SBA formats."""
    if "opportunitiesData" in data:
        ops = data["opportunitiesData"]
    elif "opportunities" in data:
        ops = data["opportunities"]
    elif "results" in data:
        ops = data["results"]
    else:
        ops = []
    
    normalized = []
    for item in ops:
        normalized.append({
            "title": (item.get("title") or item.get("noticeTitle") or item.get("solicitationNumber")),
            "solicitation_number": item.get("solicitationNumber"),
            "agency": (item.get("agency") or item.get("department") or item.get("organizationName")),
            "office": item.get("officeAddress", {}).get("city"),
            "posted": (item.get("postedDate") or item.get("posted") or item.get("publishedDate")),
            "response_deadline": (item.get("responseDeadLine") or item.get("closeDate") or item.get("close")),
            "naics_code": item.get("naicsCode"),
            "set_aside": item.get("typeOfSetAside"),
            "classification_code": item.get("classificationCode"),
            "url": (item.get("uiLink") or item.get("url") or item.get("link")),
            "description": item.get("description", "")[:200]
        })
    
    return normalized


class SBACertificationChecker:
    """Check SBA certifications via SAM.gov entity data."""
    
    @staticmethod
    def check_certifications(entity_data: Dict[str, Any]) -> Dict[str, bool]:
        """Extract certification status from SAM.gov entity data."""
        assertions = entity_data.get("assertions", {})
        goods_services = assertions.get("goodsAndServices", {})
        
        return {
            "8a_program": goods_services.get("sbaBusinessTypeCode") == "8A",
            "hubzone": goods_services.get("hubZoneCertified", False),
            "wosb": goods_services.get("womenOwnedSmallBusiness", False),
            "edwosb": goods_services.get("economicallyDisadvantagedWomenOwnedSmallBusiness", False),
            "sdvosb": goods_services.get("serviceDisabledVeteranOwnedBusiness", False),
            "small_business": goods_services.get("isSmallBusiness", False),
            "minority_owned": goods_services.get("minorityOwned", False)
        }
