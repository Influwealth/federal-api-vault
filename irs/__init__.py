"""IRS module for Federal API Vault."""
from .client import validate_ein, validate_ssn, format_ein, TaxIDValidator

__all__ = ["validate_ein", "validate_ssn", "format_ein", "TaxIDValidator"]
