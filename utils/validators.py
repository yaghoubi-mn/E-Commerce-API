import re
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    """
    Validates that the phone number is a valid Iranian phone number.
    """
    if not re.match(r'^09\d{9}$', value):
        raise ValidationError('Invalid phone number format. It must be in the format 09XXXXXXXXX.')

def validate_bank_account(value):
    """
    Validates that the bank account number is a valid number.
    This is a simple check, a more complex one might be needed.
    """
    if not value.isdigit():
        raise ValidationError('Bank account number must contain only digits.')
