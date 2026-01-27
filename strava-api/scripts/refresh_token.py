#!/usr/bin/env python3
"""
Strava Token Refresh Script

Refreshes expired access tokens using credentials from secure storage.
Secrets are stored in system keychain and not accessible to AI agents.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import requests
except ImportError:
    print("Installing requests library...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

import secure_storage

METADATA_FILE = Path.home() / ".strava" / "metadata.json"
OAUTH_TOKEN_URL = "https://www.strava.com/oauth/token"


def load_metadata() -> dict:
    """Load non-secret metadata from file."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE) as f:
            return json.load(f)
    return {}


def save_metadata(metadata: dict):
    """Save non-secret metadata to file."""
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)


def is_token_expired(metadata: dict) -> bool:
    """Check if access token is expired or about to expire."""
    expires_at = metadata.get("expires_at", 0)
    # Consider expired if less than 5 minutes remaining
    return time.time() > (expires_at - 300)


def refresh_token(force: bool = False, silent: bool = False) -> bool:
    """
    Refresh the access token.

    Returns True if token is valid (refreshed or still valid).
    """
    if not secure_storage.is_configured():
        if not silent:
            print("Error: Strava not configured.")
            print("Run setup_oauth.py first.")
        return False

    metadata = load_metadata()

    if not force and not is_token_expired(metadata):
        remaining = metadata.get("expires_at", 0) - time.time()
        if remaining > 0:
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            if not silent:
                print(f"Token is still valid for {hours}h {minutes}m")
            return True

    if not silent:
        print("Refreshing access token...")

    # Get credentials from secure storage
    creds = secure_storage.get_credentials()
    if not creds:
        if not silent:
            print("Error: Could not retrieve credentials from keychain.")
        return False

    try:
        response = requests.post(
            OAUTH_TOKEN_URL,
            data={
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "refresh_token": creds["refresh_token"],
                "grant_type": "refresh_token",
            },
        )

        if response.status_code != 200:
            if not silent:
                print(f"Error: {response.status_code}")
                try:
                    print(response.json())
                except Exception:
                    print(response.text)
            return False

        token_data = response.json()

        # Update tokens in secure storage
        secure_storage.update_tokens(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
        )

        # Update metadata
        metadata["expires_at"] = token_data["expires_at"]
        save_metadata(metadata)

        if not silent:
            print("Token refreshed successfully!")
            print(f"New token expires at: {token_data['expires_at']}")

        return True

    except Exception as e:
        if not silent:
            print(f"Error refreshing token: {e}")
        return False


def ensure_valid_token() -> bool:
    """
    Ensure we have a valid access token.
    Refreshes if necessary.

    Returns True if token is valid.
    """
    metadata = load_metadata()

    if is_token_expired(metadata):
        return refresh_token(silent=True)

    return secure_storage.is_configured()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Refresh Strava access token")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Force refresh even if not expired"
    )
    parser.add_argument(
        "--status", "-s", action="store_true", help="Show token status only"
    )

    args = parser.parse_args()

    if args.status:
        if secure_storage.is_configured():
            metadata = load_metadata()
            expires_at = metadata.get("expires_at", 0)
            remaining = expires_at - time.time()
            if remaining > 0:
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                print(f"Token status: VALID ({hours}h {minutes}m remaining)")
            else:
                print("Token status: EXPIRED")
            print(f"Athlete: {metadata.get('athlete_name', 'N/A')}")
        else:
            print("Token status: NOT CONFIGURED")
    else:
        success = refresh_token(force=args.force)
        sys.exit(0 if success else 1)
