#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Make repo imports work no matter where we run from
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

mcp = FastMCP("federal-api-vault")

WORKFLOWS = {
    "scan": "workflows.opportunity_scan",
    "nightly": "workflows.nightly_sync",
    "refresh": "workflows.entity_refresh",
}

@mcp.tool()
def list_workflows() -> list[str]:
    """List available workflows."""
    return sorted(WORKFLOWS.keys())

@mcp.tool()
def run_workflow(name: str) -> str:
    """Run a workflow by name: scan | nightly | refresh."""
    name = (name or "").strip().lower()
    if name not in WORKFLOWS:
        return f"Unknown workflow '{name}'. Available: {', '.join(sorted(WORKFLOWS))}"

    mod_path = WORKFLOWS[name]
    mod = __import__(mod_path, fromlist=["run"])
    run_fn = getattr(mod, "run", None)
    if not callable(run_fn):
        return f"Workflow module '{mod_path}' has no callable run()"

    run_fn()
    return f"OK: ran workflow '{name}'"

def main():
    # MCP servers commonly use bearer token; keep it simple & compatible
    os.environ.setdefault("MCP_BEARER_TOKEN", os.environ.get("MCP_BEARER_TOKEN", "change_me"))
    mcp.run()

if __name__ == "__main__":
    main()
