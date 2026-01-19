#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure repo root is on sys.path so imports like "import workflows" work
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

def main():
    if len(sys.argv) < 2:
        print("Usage: run.py <workflow>")
        print("Workflows: nightly | scan | refresh")
        return 2

    workflow = sys.argv[1].strip().lower()

    if workflow == "nightly":
        from workflows.nightly_sync import run
        run()
    elif workflow == "scan":
        from workflows.opportunity_scan import run
        run()
    elif workflow == "refresh":
        from workflows.entity_refresh import run
        run()
    else:
        print(f"Unknown workflow: {workflow}")
        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
