# Federal API Vault

**Automated Federal Business Data Infrastructure**  
Sovereign automation engine for SAM.gov, SBA, IRS, DOL | InfluWealth Consult LLC

---

## Overview

Federal API Vault automates access to U.S. federal business systems:

- **SAM.gov** - Entity registration, exclusions, and contract opportunities
- **SBA** - Small business contracting and certifications
- **DOL/BLS** - Labor statistics and WOTC eligibility
- **IRS** - Tax ID validation (EIN, SSN, ITIN)

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/Influwealth/federal-api-vault.git
cd federal-api-vault

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your API keys

# Test
python scripts/run.py test
```

---

## API Keys Required

| Service | Where to Get | Cost |
|---------|--------------|------|
| SAM.gov | <https://open.gsa.gov/api/entity-api/> | Free |
| DOL/BLS | <https://www.bls.gov/developers/> | Free |

---

## CLI Commands

```bash
python scripts/run.py test      # Test API connectivity
python scripts/run.py nightly   # Full sync (entities + opportunities + labor)
python scripts/run.py scan      # Scan for contract opportunities
python scripts/run.py refresh   # Refresh tracked entity registrations
```

---

## Architecture

```
federal-api-vault/
├── config.py              # Central configuration
├── utils/
│   └── http_client.py     # HTTP client with retry/cache/rate limiting
├── sam/
│   └── client.py          # SAM.gov Entity API
├── sba/
│   └── client.py          # SBA Opportunities API
├── dol/
│   └── client.py          # DOL/BLS Labor Statistics
├── irs/
│   └── client.py          # IRS Tax ID Validation
├── workflows/
│   └── implementations.py # Automated workflows
└── scripts/
    └── run.py             # CLI runner
```

---

## Python Usage

```python
# SAM.gov - Get entity info
from sam.client import SAMEntityAPI
sam = SAMEntityAPI()
entity = sam.get_entity_by_uei("ABC123DEF456")
status = sam.validate_entity_status("ABC123DEF456")

# SBA - Find opportunities
from sba.client import SBAOpportunitiesAPI
sba = SBAOpportunitiesAPI()
ops = sba.get_8a_opportunities(naics_code="541512", limit=10)

# DOL - WOTC eligibility
from dol.client import wotc_eligibility
result = wotc_eligibility({"name": "John", "age": 35, "veteran": True})

# IRS - Validate EIN
from irs.client import validate_ein
is_valid = validate_ein("12-3456789")
```

---

## Configuration Files

**data/tracked_entities.json** - Entities to monitor:

```json
{"ueis": ["ABC123DEF456", "GHI789JKL012"]}
```

**data/opportunity_filters.json** - Search criteria:

```json
{
  "naics_codes": ["541512", "541519"],
  "set_asides": ["8A", "WOSB", "HUBZone"],
  "keywords": ["software", "consulting"],
  "min_days_to_respond": 7
}
```

---

## License

Proprietary - Copyright © 2025 InfluWealth Consult LLC  
All rights reserved.

---

**Built by InfluWealth Consult LLC**  
Sovereign automation systems for modern enterprise.
