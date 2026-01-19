# Federal API Vault (WealthBridge OS)

A small, teachable repo that groups helpers for U.S. federal systems:
**SAM.gov**, **SBA**, **IRS**, **DOL**.

This is intentionally lightweight and “capsule-ready” for agent runtimes (DeepFlex / Gemini CLI / n8n).

## Repo Layout

- `sam/` — SAM.gov helpers (payload shaping, entity status normalization)
- `sba/` — opportunity extraction helpers
- `irs/` — lightweight validation helpers (ex: EIN)
- `dol/` — workforce/WOTC placeholders
- `workflows/` — orchestration entrypoints (nightly sync, scans, refresh)
- `docs/` — notes/specs (optional)
- `endpoints/` — endpoint references (optional)

## Install (Termux / Linux / macOS)

```bash
cd ~/WealthBridge/Console/Storage/federal-api-vault
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
