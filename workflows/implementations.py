"""
Production workflow implementations for Federal API Vault.
These are the orchestration layers that combine multiple APIs.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from sam.client import SAMEntityAPI, parse_entity_status
from sba.client import SBAOpportunitiesAPI, extract_opportunities
from dol.client import DOLAPI, wotc_eligibility
from irs.client import validate_ein, TaxIDValidator


class EntityRefreshWorkflow:
    """Refresh SAM.gov entity registrations for tracked businesses."""
    
    def __init__(self):
        self.sam = SAMEntityAPI()
        self.entities_file = Path("data/tracked_entities.json")
        self.entities_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_tracked_entities(self) -> List[str]:
        """Load list of UEIs to monitor."""
        if not self.entities_file.exists():
            return []
        
        try:
            with open(self.entities_file, "r") as f:
                data = json.load(f)
                return data.get("ueis", [])
        except Exception:
            return []
    
    def run(self) -> None:
        """Execute entity refresh workflow."""
        print("=== Entity Refresh Workflow ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        ueis = self.load_tracked_entities()
        print(f"Tracking {len(ueis)} entities")
        
        if not ueis:
            print("No entities tracked. Add UEIs to data/tracked_entities.json")
            return
        
        results = []
        for uei in ueis:
            print(f"\nRefreshing {uei}...")
            status = self.sam.validate_entity_status(uei)
            results.append(status)
            
            if not status.get("is_active"):
                print(f"  ⚠️  INACTIVE: {status.get('legal_name')}")
            
            if status.get("has_exclusions"):
                print(f"  ⚠️  EXCLUSIONS: {status.get('exclusion_count')} found")
        
        output_file = Path("data/entity_refresh_results.json")
        with open(output_file, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "results": results}, f, indent=2)
        
        print(f"\n✅ Results saved to {output_file}")


class OpportunityScanWorkflow:
    """Scan for relevant federal contracting opportunities."""
    
    def __init__(self):
        self.sba = SBAOpportunitiesAPI()
        self.config_file = Path("data/opportunity_filters.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_filters(self) -> Dict[str, Any]:
        """Load opportunity search filters."""
        if not self.config_file.exists():
            return {
                "naics_codes": [],
                "set_asides": ["SBA", "8A", "WOSB"],
                "keywords": [],
                "min_days_to_respond": 7
            }
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"naics_codes": [], "set_asides": []}
    
    def run(self) -> None:
        """Execute opportunity scan workflow."""
        print("=== Opportunity Scan Workflow ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        filters = self.load_filters()
        all_opportunities = []
        
        for naics in filters.get("naics_codes", []):
            print(f"\nSearching NAICS {naics}...")
            for set_aside in filters.get("set_asides", []):
                ops = self.sba.search_opportunities(naics_code=naics, set_aside=set_aside, limit=20)
                all_opportunities.extend(ops)
        
        normalized = extract_opportunities({"opportunitiesData": all_opportunities})
        
        print(f"\n✅ {len(normalized)} opportunities found")
        
        output_file = Path("data/opportunities_scan_results.json")
        with open(output_file, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "opportunities": normalized}, f, indent=2)


class NightlySyncWorkflow:
    """Combined nightly sync of all federal data sources."""
    
    def __init__(self):
        self.sam = SAMEntityAPI()
        self.sba = SBAOpportunitiesAPI()
        self.dol = DOLAPI()
    
    def run(self) -> None:
        """Execute comprehensive nightly sync."""
        print("=" * 50)
        print("NIGHTLY SYNC WORKFLOW")
        print("=" * 50)
        print(f"Started: {datetime.now().isoformat()}\n")
        
        print("[1/3] Refreshing entity data...")
        EntityRefreshWorkflow().run()
        
        print("\n[2/3] Scanning opportunities...")
        OpportunityScanWorkflow().run()
        
        print("\n[3/3] Updating labor statistics...")
        print("✅ Labor statistics placeholder")
        
        print(f"\n{'=' * 50}")
        print(f"Completed: {datetime.now().isoformat()}")


def run_nightly_sync():
    NightlySyncWorkflow().run()

def run_opportunity_scan():
    OpportunityScanWorkflow().run()

def run_entity_refresh():
    EntityRefreshWorkflow().run()
