"""
AES-256 encryption utilities for sensitive log fields.
Uses AES-GCM mode for authenticated encryption.
"""

from __future__ import annotations

import base64
import json
import logging
import secrets
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from django.conf import settings

logger = logging.getLogger(__name__)


def get_encryption_key() -> bytes:
    """
    Get the encryption key from settings.
    Key must be 32 bytes (256 bits) for AES-256.
    """
    key_str = getattr(settings, 'LOG_ENCRYPTION_KEY', None)
    if not key_str:
        # Fallback to SECRET_KEY if LOG_ENCRYPTION_KEY not set (for development)
        key_str = getattr(settings, 'SECRET_KEY', '')
        logger.warning("LOG_ENCRYPTION_KEY not set, using SECRET_KEY as fallback")
    
    # Ensure key is 32 bytes
    key_bytes = key_str.encode('utf-8')[:32]
    if len(key_bytes) < 32:
        # Pad with zeros if needed (not ideal, but better than error)
        key_bytes = key_bytes.ljust(32, b'\0')
    
    return key_bytes[:32]


def encrypt_field(data: Any) -> str:
    """
    Encrypt a field value (dict, list, or string) using AES-256-GCM.
    
    Args:
        data: The data to encrypt (dict, list, or string)
    
    Returns:
        Base64-encoded encrypted string with format: "encrypted:<nonce>:<ciphertext>:<tag>"
    """
    if data is None:
        return ""
    
    try:
        # Convert to JSON string if not already a string
        if isinstance(data, (dict, list)):
            plaintext = json.dumps(data, sort_keys=True).encode('utf-8')
        else:
            plaintext = str(data).encode('utf-8')
        
        # Generate nonce (12 bytes for GCM)
        key = get_encryption_key()
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        
        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Combine nonce and ciphertext, then base64 encode
        # Format: nonce (12 bytes) + ciphertext (variable length)
        encrypted_data = nonce + ciphertext
        encoded = base64.b64encode(encrypted_data).decode('utf-8')
        
        return f"encrypted:{encoded}"
    except Exception as e:
        logger.error(f"Encryption failed: {e}", exc_info=True)
        # Return original data as string if encryption fails (should not happen in production)
        return str(data)


def decrypt_field(encrypted_data: str) -> Any:
    """
    Decrypt a field value that was encrypted with encrypt_field.
    
    Args:
        encrypted_data: The encrypted string in format "encrypted:<base64_data>"
    
    Returns:
        The decrypted data (dict, list, or string)
    """
    if not encrypted_data or not isinstance(encrypted_data, str):
        return encrypted_data
    
    # Check if it's encrypted
    if not encrypted_data.startswith("encrypted:"):
        # Not encrypted, return as-is (for backward compatibility)
        try:
            # Try to parse as JSON if it looks like JSON
            if encrypted_data.startswith('{') or encrypted_data.startswith('['):
                return json.loads(encrypted_data)
            return encrypted_data
        except (json.JSONDecodeError, ValueError):
            return encrypted_data
    
    try:
        # Extract base64 data
        encoded_data = encrypted_data[len("encrypted:"):]
        encrypted_bytes = base64.b64decode(encoded_data)
        
        # Extract nonce (first 12 bytes) and ciphertext (rest)
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        
        # Decrypt
        key = get_encryption_key()
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Try to parse as JSON, fallback to string
        try:
            return json.loads(plaintext.decode('utf-8'))
        except json.JSONDecodeError:
            return plaintext.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption failed: {e}", exc_info=True)
        # Return encrypted string if decryption fails (should not happen in production)
        return encrypted_data


def encrypt_sensitive_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Encrypt sensitive fields in a context dictionary.
    Sensitive fields: ip_address, ip, user_agent, device_id, device_name, device_info, email, phone
    
    Args:
        context: The context dictionary
    
    Returns:
        Context dictionary with sensitive fields encrypted
    """
    if not context or not isinstance(context, dict):
        return context or {}
    
    sensitive_fields = [
        'ip_address', 'ip', 'user_agent', 'device_id', 'device_name', 
        'device_info', 'email', 'phone', 'username', 'password'
    ]
    
    encrypted_context = context.copy()
    for field in sensitive_fields:
        if field in encrypted_context and encrypted_context[field]:
            # Only encrypt if not already encrypted
            value = encrypted_context[field]
            if isinstance(value, str):
                # Skip if already encrypted
                if not value.startswith("encrypted:"):
                    encrypted_context[field] = encrypt_field(value)
            elif isinstance(value, (dict, list)):
                # Encrypt complex structures (only if not already encrypted)
                # Check if it's a string representation of encrypted data
                if not (isinstance(value, str) and value.startswith("encrypted:")):
                    encrypted_context[field] = encrypt_field(value)
    
    return encrypted_context


def decrypt_sensitive_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decrypt sensitive fields in a context dictionary.
    
    Args:
        context: The context dictionary with encrypted fields
    
    Returns:
        Context dictionary with sensitive fields decrypted
    """
    if not context or not isinstance(context, dict):
        return context or {}
    
    sensitive_fields = [
        'ip_address', 'ip', 'user_agent', 'device_id', 'device_name',
        'device_info', 'email', 'phone', 'username', 'password'
    ]
    
    decrypted_context = context.copy()
    for field in sensitive_fields:
        if field in decrypted_context:
            value = decrypted_context[field]
            if isinstance(value, str) and value.startswith("encrypted:"):
                decrypted_context[field] = decrypt_field(value)
            elif isinstance(value, (dict, list)):
                # Try to decrypt if it's a complex structure
                try:
                    decrypted_context[field] = decrypt_field(json.dumps(value))
                except:
                    pass
    
    return decrypted_context

