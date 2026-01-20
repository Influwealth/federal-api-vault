#!/usr/bin/env python3
"""
Federal API Vault - Workflow Runner
Execute automated workflows for federal data synchronization.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def main():
    """Main entry point for workflow execution."""
    from config import Config
    
    if len(sys.argv) < 2:
        print("Federal API Vault - Workflow Runner")
        print("\nUsage: python scripts/run.py <workflow>")
        print("\nAvailable workflows:")
        print("  nightly   - Run complete nightly sync")
        print("  scan      - Scan for new opportunities")
        print("  refresh   - Refresh tracked entities")
        print("  test      - Run API connectivity test")
        return 2
    
    workflow = sys.argv[1].strip().lower()
    
    from workflows.implementations import (
        run_nightly_sync,
        run_opportunity_scan,
        run_entity_refresh
    )
    
    if workflow == "nightly":
        run_nightly_sync()
    elif workflow == "scan":
        run_opportunity_scan()
    elif workflow == "refresh":
        run_entity_refresh()
    elif workflow == "test":
        run_api_test()
    else:
        print(f"❌ Unknown workflow: {workflow}")
        return 2
    
    return 0


def run_api_test():
    """Quick connectivity test for all APIs."""
    print("=" * 50)
    print("API CONNECTIVITY TEST")
    print("=" * 50)
    
    from sam.client import SAMEntityAPI
    from sba.client import SBAOpportunitiesAPI
    from dol.client import DOLAPI
    from irs.client import validate_ein
    
    print("\n[SAM.gov]")
    try:
        sam = SAMEntityAPI()
        print("✅ SAM.gov client initialized")
    except Exception as e:
        print(f"❌ SAM.gov error: {e}")
    
    print("\n[SBA Opportunities]")
    try:
        sba = SBAOpportunitiesAPI()
        print("✅ SBA client initialized")
    except Exception as e:
        print(f"❌ SBA error: {e}")
    
    print("\n[DOL/BLS]")
    try:
        dol = DOLAPI()
        print("✅ DOL/BLS client initialized")
    except Exception as e:
        print(f"❌ DOL/BLS error: {e}")
    
    print("\n[IRS Validation]")
    test_ein = "12-3456789"
    if validate_ein(test_ein):
        print("✅ IRS EIN validation working")
    else:
        print("❌ IRS validation failed")
    
    print("\n" + "=" * 50)
    print("Test complete")


if __name__ == "__main__":
    raise SystemExit(main())
