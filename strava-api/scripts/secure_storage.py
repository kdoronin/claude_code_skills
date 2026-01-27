#!/usr/bin/env python3
"""
Secure Storage Module

Stores secrets in system keychain (macOS Keychain / Linux Secret Service).
AI agents cannot read these values directly - only the scripts can access them
at runtime without exposing the values.
"""

import subprocess
import sys
import platform

SERVICE_NAME = "strava-api-credentials"

# Secret keys stored in keychain
SECRET_KEYS = ["client_id", "client_secret", "access_token", "refresh_token"]


def _get_platform():
    """Detect platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


# =============================================================================
# macOS Keychain Implementation
# =============================================================================

def _macos_set_secret(key: str, value: str) -> bool:
    """Store secret in macOS Keychain."""
    # Delete existing entry first (ignore errors)
    subprocess.run(
        ["security", "delete-generic-password", "-s", SERVICE_NAME, "-a", key],
        capture_output=True,
    )
    # Add new entry
    result = subprocess.run(
        [
            "security",
            "add-generic-password",
            "-s", SERVICE_NAME,
            "-a", key,
            "-w", value,
            "-U",  # Update if exists
        ],
        capture_output=True,
    )
    return result.returncode == 0


def _macos_get_secret(key: str) -> str | None:
    """Retrieve secret from macOS Keychain."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", SERVICE_NAME, "-a", key, "-w"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def _macos_delete_secret(key: str) -> bool:
    """Delete secret from macOS Keychain."""
    result = subprocess.run(
        ["security", "delete-generic-password", "-s", SERVICE_NAME, "-a", key],
        capture_output=True,
    )
    return result.returncode == 0


def _macos_has_secret(key: str) -> bool:
    """Check if secret exists in macOS Keychain."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", SERVICE_NAME, "-a", key],
        capture_output=True,
    )
    return result.returncode == 0


# =============================================================================
# Linux Secret Service Implementation (using secret-tool)
# =============================================================================

def _linux_set_secret(key: str, value: str) -> bool:
    """Store secret in Linux Secret Service."""
    try:
        result = subprocess.run(
            ["secret-tool", "store", "--label", f"Strava {key}", "service", SERVICE_NAME, "key", key],
            input=value.encode(),
            capture_output=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: secret-tool not found. Install libsecret-tools.")
        return False


def _linux_get_secret(key: str) -> str | None:
    """Retrieve secret from Linux Secret Service."""
    try:
        result = subprocess.run(
            ["secret-tool", "lookup", "service", SERVICE_NAME, "key", key],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        return None


def _linux_delete_secret(key: str) -> bool:
    """Delete secret from Linux Secret Service."""
    try:
        result = subprocess.run(
            ["secret-tool", "clear", "service", SERVICE_NAME, "key", key],
            capture_output=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _linux_has_secret(key: str) -> bool:
    """Check if secret exists in Linux Secret Service."""
    return _linux_get_secret(key) is not None


# =============================================================================
# Public API
# =============================================================================

def set_secret(key: str, value: str) -> bool:
    """
    Store a secret securely in system keychain.

    Args:
        key: Secret identifier (e.g., 'access_token')
        value: Secret value

    Returns:
        True if successful
    """
    plat = _get_platform()
    if plat == "macos":
        return _macos_set_secret(key, value)
    elif plat == "linux":
        return _linux_set_secret(key, value)
    else:
        print(f"Unsupported platform: {platform.system()}")
        return False


def get_secret(key: str) -> str | None:
    """
    Retrieve a secret from system keychain.

    IMPORTANT: This function returns the secret value. Do not print or log it!

    Args:
        key: Secret identifier

    Returns:
        Secret value or None if not found
    """
    plat = _get_platform()
    if plat == "macos":
        return _macos_get_secret(key)
    elif plat == "linux":
        return _linux_get_secret(key)
    else:
        return None


def delete_secret(key: str) -> bool:
    """Delete a secret from system keychain."""
    plat = _get_platform()
    if plat == "macos":
        return _macos_delete_secret(key)
    elif plat == "linux":
        return _linux_delete_secret(key)
    else:
        return False


def has_secret(key: str) -> bool:
    """Check if a secret exists in system keychain."""
    plat = _get_platform()
    if plat == "macos":
        return _macos_has_secret(key)
    elif plat == "linux":
        return _linux_has_secret(key)
    else:
        return False


def store_credentials(
    client_id: str,
    client_secret: str,
    access_token: str,
    refresh_token: str,
) -> bool:
    """Store all Strava credentials securely."""
    success = True
    success &= set_secret("client_id", client_id)
    success &= set_secret("client_secret", client_secret)
    success &= set_secret("access_token", access_token)
    success &= set_secret("refresh_token", refresh_token)
    return success


def get_credentials() -> dict | None:
    """
    Retrieve all Strava credentials from keychain.

    Returns dict with keys: client_id, client_secret, access_token, refresh_token
    or None if any credential is missing.
    """
    creds = {}
    for key in SECRET_KEYS:
        value = get_secret(key)
        if value is None:
            return None
        creds[key] = value
    return creds


def update_tokens(access_token: str, refresh_token: str) -> bool:
    """Update access and refresh tokens."""
    success = set_secret("access_token", access_token)
    success &= set_secret("refresh_token", refresh_token)
    return success


def delete_all_credentials() -> bool:
    """Delete all stored credentials."""
    success = True
    for key in SECRET_KEYS:
        success &= delete_secret(key)
    return success


def is_configured() -> bool:
    """Check if all required credentials are stored."""
    for key in SECRET_KEYS:
        if not has_secret(key):
            return False
    return True


def get_platform_info() -> str:
    """Get information about the secure storage backend."""
    plat = _get_platform()
    if plat == "macos":
        return "macOS Keychain"
    elif plat == "linux":
        return "Linux Secret Service (libsecret)"
    else:
        return f"Unsupported ({platform.system()})"


if __name__ == "__main__":
    # Test the module
    print(f"Platform: {get_platform_info()}")
    print(f"Configured: {is_configured()}")

    if is_configured():
        print("\nStored credentials:")
        for key in SECRET_KEYS:
            has = has_secret(key)
            print(f"  {key}: {'[SET]' if has else '[NOT SET]'}")
