"""
DOL Bureau of Labor Statistics API client.
Docs: https://www.bls.gov/developers/api_signature.htm
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.http_client import DOLClient
from typing import List, Dict, Any
from config import Config


class DOLAPI:
    """Department of Labor BLS data API wrapper."""
    
    def __init__(self):
        self.client = DOLClient()
    
    def get_series_data(self, series_ids: List[str], start_year: int, end_year: int) -> Dict[str, Any]:
        """Retrieve time series data from BLS."""
        try:
            payload = {
                "seriesid": series_ids,
                "startyear": str(start_year),
                "endyear": str(end_year),
                "registrationkey": Config.DOL_API_KEY
            }
            
            response = self.client.session.post(
                f"{Config.DOL_BASE_URL}/timeseries/data/",
                json=payload,
                headers=self.client.session.headers,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            print(f"Error fetching BLS series {series_ids}: {e}")
            return {"status": "REQUEST_FAILED", "message": str(e)}
    
    def get_unemployment_rate(self, area_code: str, year: int) -> float:
        """Get unemployment rate for a specific area."""
        series_id = f"LAUS{area_code}03"
        data = self.get_series_data([series_id], year, year)
        
        if data.get("status") == "REQUEST_SUCCEEDED":
            series = data.get("Results", {}).get("series", [])
            if series and len(series) > 0:
                latest = series[0].get("data", [])
                if latest:
                    return float(latest[0].get("value", 0))
        
        return 0.0
    
    def get_industry_employment(self, naics_code: str, year: int) -> Dict[str, Any]:
        """Get employment data for specific industry."""
        series_id = f"CES{naics_code}01"
        data = self.get_series_data([series_id], year, year)
        
        result = {
            "naics": naics_code,
            "year": year,
            "employment": 0,
            "data_points": []
        }
        
        if data.get("status") == "REQUEST_SUCCEEDED":
            series = data.get("Results", {}).get("series", [])
            if series:
                result["data_points"] = series[0].get("data", [])
                if result["data_points"]:
                    result["employment"] = int(result["data_points"][0].get("value", "0").replace(",", ""))
        
        return result


def wotc_eligibility(applicant: dict) -> dict:
    """Work Opportunity Tax Credit eligibility check."""
    age = int(applicant.get("age", 0) or 0)
    categories = []
    max_credit = 0
    
    # Veterans
    if applicant.get("veteran"):
        categories.append("veteran")
        if applicant.get("unemployment_months", 0) >= 6:
            categories.append("veteran_long_term_unemployed")
            max_credit = max(max_credit, 9600)
        else:
            max_credit = max(max_credit, 2400)
    
    # SNAP recipients
    if applicant.get("snap_recipient"):
        if 18 <= age <= 39:
            categories.append("snap_recipient")
            max_credit = max(max_credit, 2400)
    
    # Ex-felon
    if applicant.get("felony_conviction"):
        categories.append("ex_felon")
        max_credit = max(max_credit, 2400)
    
    # Long-term unemployment
    if applicant.get("unemployment_months", 0) >= 6:
        categories.append("long_term_unemployed")
        max_credit = max(max_credit, 2400)
    
    # Vocational rehabilitation
    if applicant.get("vocational_rehab"):
        categories.append("vocational_rehabilitation")
        max_credit = max(max_credit, 2400)
    
    # Summer youth (16-17 years old)
    if 16 <= age <= 17:
        categories.append("summer_youth")
        max_credit = max(max_credit, 1200)
    
    return {
        "name": applicant.get("name"),
        "eligible": len(categories) > 0,
        "categories": categories,
        "max_credit_usd": max_credit,
        "age": age
    }
