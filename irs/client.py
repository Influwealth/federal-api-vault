"""
IRS data validation and public record access.
Note: IRS has limited public APIs. Most data requires professional access.
"""
import re
from typing import Optional, Dict, Any


def validate_ein(ein: str) -> bool:
    """Validate Employer Identification Number format."""
    ein = (ein or "").replace("-", "").replace(" ", "").strip()
    
    if len(ein) != 9 or not ein.isdigit():
        return False
    
    prefix = int(ein[:2])
    invalid = {7, 8, 9, 17, 18, 19, 28, 29, 49, 69, 70, 78, 79, 89}
    
    return prefix not in invalid and 1 <= prefix <= 99


def validate_ssn(ssn: str) -> bool:
    """Validate Social Security Number format."""
    ssn = (ssn or "").replace("-", "").replace(" ", "").strip()
    
    if len(ssn) != 9 or not ssn.isdigit():
        return False
    
    area = int(ssn[:3])
    group = int(ssn[3:5])
    serial = int(ssn[5:])
    
    if area == 0 or area == 666 or area >= 900:
        return False
    
    if group == 0:
        return False
    
    if serial == 0:
        return False
    
    return True


def format_ein(ein: str) -> str:
    """Format EIN with proper dash: XX-XXXXXXX"""
    ein = ein.replace("-", "").strip()
    if len(ein) == 9 and ein.isdigit():
        return f"{ein[:2]}-{ein[2:]}"
    return ein


class TaxIDValidator:
    """Validation for various tax identifiers."""
    
    @staticmethod
    def validate_itin(itin: str) -> bool:
        """Validate Individual Taxpayer Identification Number."""
        itin = itin.replace("-", "").strip()
        if len(itin) != 9 or not itin.isdigit():
            return False
        
        if itin[0] != '9':
            return False
        
        middle = int(itin[3:5])
        valid_ranges = (
            (70 <= middle <= 88) or
            (90 <= middle <= 92) or
            (94 <= middle <= 99)
        )
        
        return valid_ranges
    
    @staticmethod
    def identify_tax_id_type(tax_id: str) -> str:
        """Determine type of tax ID."""
        tax_id = tax_id.replace("-", "").strip()
        
        if len(tax_id) != 9 or not tax_id.isdigit():
            return "UNKNOWN"
        
        # ITIN starts with 9
        if tax_id[0] == '9':
            middle = int(tax_id[3:5])
            if (70 <= middle <= 88) or (90 <= middle <= 92) or (94 <= middle <= 99):
                return "ITIN"
        
        if validate_ein(tax_id):
            return "EIN"
        
        if validate_ssn(tax_id):
            return "SSN"
        
        return "UNKNOWN"
