"""
Configuration management for Federal API Vault.
Loads from .env and provides typed access to settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


class Config:
    """Central configuration for all federal API integrations."""
    
    # SAM.gov
    SAM_API_KEY = os.getenv("SAM_API_KEY", "")
    SAM_BASE_URL = os.getenv("SAM_BASE_URL", "https://api.sam.gov/entity-information/v3/entities")
    
    # SBA
    SBA_API_KEY = os.getenv("SBA_API_KEY", "")
    SBA_BASE_URL = os.getenv("SBA_BASE_URL", "https://api.sba.gov/v1")
    
    # IRS
    IRS_API_KEY = os.getenv("IRS_API_KEY", "")
    IRS_BASE_URL = os.getenv("IRS_BASE_URL", "https://irs.gov/api")
    
    # DOL
    DOL_API_KEY = os.getenv("DOL_API_KEY", "")
    DOL_BASE_URL = os.getenv("DOL_BASE_URL", "https://api.bls.gov/publicAPI/v2")
    
    # General
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Rate limits
    RATE_LIMIT_SAM = int(os.getenv("RATE_LIMIT_SAM", "100"))
    RATE_LIMIT_SBA = int(os.getenv("RATE_LIMIT_SBA", "60"))
    RATE_LIMIT_IRS = int(os.getenv("RATE_LIMIT_IRS", "30"))
    RATE_LIMIT_DOL = int(os.getenv("RATE_LIMIT_DOL", "500"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/federal-api-vault.log")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/vault.db")

    @classmethod
    def validate(cls) -> list[str]:
        """Returns list of missing required credentials."""
        missing = []
        if not cls.SAM_API_KEY:
            missing.append("SAM_API_KEY")
        if not cls.DOL_API_KEY:
            missing.append("DOL_API_KEY")
        return missing

    @classmethod
    def is_ready(cls) -> bool:
        """Check if minimal credentials are configured."""
        return len(cls.validate()) == 0
