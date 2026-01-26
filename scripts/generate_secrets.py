#!/usr/bin/env python3
"""
Generate secure secrets for production deployment.

This script generates cryptographically secure random keys for:
- DJANGO_SECRET_KEY (50+ characters)
- JWT_SIGNING_KEY (32+ characters)
- JWT_SECRET (32+ characters)
- LOG_ENCRYPTION_KEY (exactly 32 bytes for AES-256)

Usage:
    python scripts/generate_secrets.py

Output can be copied directly into your .env file.
"""

import secrets
import base64
import sys


def generate_secret_key(length=43):
    """Generate a secure random key using URL-safe base64 encoding."""
    return secrets.token_urlsafe(length)


def generate_encryption_key():
    """Generate exactly 32 bytes (256 bits) for AES-256 encryption."""
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')


def main():
    """Generate and display all required secrets."""
    print("=" * 70)
    print("SECURE SECRETS GENERATOR")
    print("=" * 70)
    print()
    print("IMPORTANT: Keep these secrets secure and never commit them to version control!")
    print()
    print("-" * 70)
    print()
    
    # Generate Django SECRET_KEY (50+ characters)
    django_secret = generate_secret_key(43)  # 43 bytes = ~57 characters in base64
    print(f"DJANGO_SECRET_KEY={django_secret}")
    print(f"  Length: {len(django_secret)} characters ✓")
    print()
    
    # Generate JWT Signing Key
    jwt_signing_key = generate_secret_key(32)
    print(f"JWT_SIGNING_KEY={jwt_signing_key}")
    print(f"  Length: {len(jwt_signing_key)} characters ✓")
    print()
    
    # Generate JWT Secret
    jwt_secret = generate_secret_key(32)
    print(f"JWT_SECRET={jwt_secret}")
    print(f"  Length: {len(jwt_secret)} characters ✓")
    print()
    
    # Generate Log Encryption Key (exactly 32 bytes)
    log_encryption_key = generate_encryption_key()
    print(f"LOG_ENCRYPTION_KEY={log_encryption_key}")
    # Verify it's exactly 32 bytes when decoded
    decoded_bytes = base64.b64decode(log_encryption_key)
    print(f"  Length: {len(decoded_bytes)} bytes (exactly 32 bytes for AES-256) ✓")
    print()
    
    # Generate TURN Shared Secret (optional but recommended)
    turn_secret = generate_secret_key(32)
    print(f"TURN_SHARED_SECRET={turn_secret}")
    print(f"  Length: {len(turn_secret)} characters ✓")
    print()
    
    print("-" * 70)
    print()
    print("Copy these values into your .env file, replacing placeholder values.")
    print("Do NOT use these example keys in production - generate new ones!")
    print()
    print("=" * 70)
    
    # Return success
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError generating secrets: {e}", file=sys.stderr)
        sys.exit(1)

