from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

def validate_amka(value):
    """Validate AMKA (Greek Social Security Number)"""
    if not re.match(r'^\d{11}$', str(value)):
        raise ValidationError(_('Ο ΑΜΚΑ πρέπει να αποτελείται από 11 ψηφία.'))
    
    # Add more specific AMKA validation rules here
    return value

def validate_afm(value):
    """Validate AFM (Greek Tax Number)"""
    if not re.match(r'^\d{9}$', str(value)):
        raise ValidationError(_('Το ΑΦΜ πρέπει να αποτελείται από 9 ψηφία.'))
    
    # Validate AFM checksum
    digits = [int(d) for d in str(value)]
    checksum = sum(digits[i] * (2 ** (8 - i)) for i in range(8)) % 11
    checksum = checksum % 10
    
    if checksum != digits[8]:
        raise ValidationError(_('Μη έγκυρο ΑΦΜ.'))
    
    return value

def validate_phone(value):
    """Validate Greek phone numbers"""
    # Remove spaces and common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', str(value))
    
    # Check for valid formats
    if not re.match(r'^(?:(?:\+|00)30)?[2-9]\d{9}$', cleaned):
        raise ValidationError(_('Μη έγκυρος αριθμός τηλεφώνου.'))
    
    return cleaned

def validate_postal_code(value):
    """Validate Greek postal codes"""
    if not re.match(r'^\d{5}$', str(value)):
        raise ValidationError(_('Ο ταχυδρομικός κώδικας πρέπει να αποτελείται από 5 ψηφία.'))
    return value

def clean_text(value):
    """Clean and normalize text input"""
    if value:
        # Remove extra whitespace
        value = ' '.join(value.split())
        # Capitalize first letter of each word for names
        value = value.title()
    return value 