#!/usr/bin/env python3
"""
Interactive Strava OAuth Setup Script

Guides user through the complete OAuth flow and saves credentials
securely in system keychain (not accessible to AI agents).
"""

import json
import os
import sys
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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

# Non-secret metadata file (no sensitive data here)
CONFIG_DIR = Path.home() / ".strava"
METADATA_FILE = CONFIG_DIR / "metadata.json"

OAUTH_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://www.strava.com/oauth/token"

DEFAULT_SCOPES = "read,read_all,profile:read_all,profile:write,activity:read,activity:read_all,activity:write"


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print("=" * 60)


def print_step(step: int, text: str):
    """Print step indicator."""
    print(f"\n[Step {step}] {text}")
    print("-" * 40)


def load_metadata() -> dict:
    """Load non-secret metadata."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE) as f:
            return json.load(f)
    return {}


def save_metadata(metadata: dict):
    """Save non-secret metadata to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)


def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def get_secret_input(prompt: str) -> str:
    """Get secret input (no echo if possible)."""
    try:
        import getpass
        return getpass.getpass(f"{prompt}: ")
    except Exception:
        return input(f"{prompt}: ").strip()


def setup_oauth():
    """Main OAuth setup flow."""
    print_header("Strava API OAuth Setup")
    print(f"\nSecure storage: {secure_storage.get_platform_info()}")

    metadata = load_metadata()

    # Check if already configured
    if secure_storage.is_configured():
        print("\nExisting configuration found!")
        print(f"  Athlete: {metadata.get('athlete_name', 'N/A')}")
        print(f"  Athlete ID: {metadata.get('athlete_id', 'N/A')}")
        print(f"  Token expires at: {metadata.get('expires_at', 'N/A')}")
        print("\n  (Secrets stored securely in system keychain)")

        choice = get_input("\nReconfigure? (y/n)", "n")
        if choice.lower() != "y":
            print("\nKeeping existing configuration.")
            return True

    # Step 1: Get Client credentials
    print_step(1, "Enter Strava API Application Credentials")
    print("\nGet these from: https://www.strava.com/settings/api")
    print("(Create an app if you don't have one)\n")
    print("NOTE: Your credentials will be stored securely in system keychain")
    print("      and will NOT be accessible to AI agents.\n")

    client_id = get_input("Client ID")
    client_secret = get_secret_input("Client Secret (hidden input)")

    if not client_id or not client_secret:
        print("\nError: Client ID and Secret are required!")
        sys.exit(1)

    # Step 2: Authorization
    print_step(2, "Authorize with Strava")

    auth_url = (
        f"{OAUTH_AUTHORIZE_URL}?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"redirect_uri=http://localhost&"
        f"scope={DEFAULT_SCOPES}"
    )

    print("\nOpening browser for authorization...")
    print(f"\nIf browser doesn't open, visit this URL:\n{auth_url}\n")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("After authorizing, you'll be redirected to a localhost URL.")
    print("The page won't load (that's normal).")
    print("\nCopy the ENTIRE URL from your browser's address bar.")

    redirect_url = get_input("\nPaste the redirect URL here")

    # Extract authorization code
    try:
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        auth_code = params.get("code", [None])[0]

        if not auth_code:
            print("\nError: Could not extract authorization code from URL!")
            print("Make sure you copied the entire URL including ?code=...")
            sys.exit(1)
    except Exception as e:
        print(f"\nError parsing URL: {e}")
        sys.exit(1)

    # Step 3: Exchange code for tokens
    print_step(3, "Exchanging code for access token...")

    try:
        response = requests.post(
            OAUTH_TOKEN_URL,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": auth_code,
                "grant_type": "authorization_code",
            },
        )

        if response.status_code != 200:
            print(f"\nError: {response.status_code}")
            print(response.json())
            sys.exit(1)

        token_data = response.json()

    except Exception as e:
        print(f"\nError exchanging token: {e}")
        sys.exit(1)

    # Step 4: Store credentials securely
    print_step(4, "Storing credentials securely...")

    # Store secrets in keychain
    success = secure_storage.store_credentials(
        client_id=client_id,
        client_secret=client_secret,
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
    )

    if not success:
        print("\nError: Failed to store credentials in keychain!")
        sys.exit(1)

    print("  Secrets stored in system keychain")

    # Store non-secret metadata in file
    metadata = {
        "athlete_id": token_data.get("athlete", {}).get("id"),
        "athlete_name": f"{token_data.get('athlete', {}).get('firstname', '')} {token_data.get('athlete', {}).get('lastname', '')}".strip(),
        "expires_at": token_data["expires_at"],
    }
    save_metadata(metadata)
    print(f"  Metadata saved to: {METADATA_FILE}")

    # Step 5: Verify connection
    print_step(5, "Verifying connection...")

    try:
        verify_response = requests.get(
            "https://www.strava.com/api/v3/athlete",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        if verify_response.status_code == 200:
            athlete = verify_response.json()
            print(f"\nConnected successfully!")
            print(f"  Athlete: {athlete.get('firstname')} {athlete.get('lastname')}")
            print(f"  ID: {athlete.get('id')}")
        else:
            print(f"\nWarning: Verification failed ({verify_response.status_code})")

    except Exception as e:
        print(f"\nWarning: Could not verify connection: {e}")

    # Print summary
    print_header("Setup Complete!")
    print(f"""
Your Strava API is now configured.

SECURITY:
  - Secrets (tokens, client_secret) stored in: {secure_storage.get_platform_info()}
  - Non-secret metadata stored in: {METADATA_FILE}
  - AI agents CANNOT read your secrets from keychain

ACCESS:
  - Athlete: {metadata['athlete_name']}
  - Athlete ID: {metadata['athlete_id']}

Note: Access tokens expire after 6 hours.
      Tokens are refreshed automatically by the API client.
""")

    return True


if __name__ == "__main__":
    setup_oauth()
