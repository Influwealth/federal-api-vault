# Federal API Vault — SAP Integration

## Role in Sovereign Architecture
Federal API Vault provides data connectors to US federal data sources for the
WealthBridge OS prediction and compliance layers.

## Data Sources
- IRS e-file API (tax filing)
- FFIEC (banking regulation data)
- SEC EDGAR (financial disclosures)
- USDA (agricultural/cannabis/hemp data for CannaBIIQ)
- EPA (environmental protection, epa-electronic-protection-agent)
- Federal Reserve (economic indicators)

## SAP Node ID: `federal-api-vault`

## Port: 7795 (planned)

## Integration Points
| Consumer | Data Used |
|----------|-----------|
| wealthbridge-tax-stack | IRS e-file, tax tables |
| epa-electronic-protection-agent | EPA data feeds |
| cannabiiq-data-connector | USDA hemp/cannabis regulations |
| qre-agent-platform (Caffeine) | Economic indicators for prediction |

## Security
- All federal API keys stored in environment variables
- Never committed to git
- Rotated quarterly
- See `.env.example` for required variables

## SAP Headers (Python)
```python
sap_headers = {
    "x-sap-node-id": "federal-api-vault",
    "x-sap-trace-id": str(uuid.uuid4()),
    "x-sap-version": "1.0",
}
```

## Branch
All synthesis work: `claude/deepflex-argus-synthesis-jWjmO`
