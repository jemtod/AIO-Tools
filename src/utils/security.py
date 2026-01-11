"""
Security utility functions
"""

import secrets
import string


def generate_random_password(length: int = 16) -> str:
    """Generate random secure password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def generate_api_key(length: int = 32) -> str:
    """Generate random API key"""
    characters = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(characters) for _ in range(length))
    return key


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data (e.g., passwords, tokens)"""
    if len(data) <= visible_chars:
        return '*' * len(data)
    
    visible = data[-visible_chars:]
    masked = '*' * (len(data) - visible_chars)
    return masked + visible
