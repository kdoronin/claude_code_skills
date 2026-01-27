#!/usr/bin/env python3
"""
Strava API Client

Universal client for making Strava API requests with automatic token management.
Credentials are stored securely in system keychain - not accessible to AI agents.
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
BASE_URL = "https://www.strava.com/api/v3"
OAUTH_TOKEN_URL = "https://www.strava.com/oauth/token"


class StravaClient:
    """
    Strava API client with automatic token refresh.

    Credentials are stored in system keychain and never exposed.
    """

    def __init__(self):
        self._metadata = self._load_metadata()
        self._ensure_configured()
        self._ensure_valid_token()

    def _load_metadata(self) -> dict:
        """Load non-secret metadata from file."""
        if METADATA_FILE.exists():
            with open(METADATA_FILE) as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save non-secret metadata to file."""
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(METADATA_FILE, "w") as f:
            json.dump(self._metadata, f, indent=2)

    def _ensure_configured(self):
        """Ensure Strava is configured."""
        if not secure_storage.is_configured():
            print("Error: Strava not configured.")
            print("Run: python3 scripts/setup_oauth.py")
            sys.exit(1)

    def _is_token_expired(self) -> bool:
        """Check if token is expired."""
        expires_at = self._metadata.get("expires_at", 0)
        return time.time() > (expires_at - 300)

    def _refresh_token(self):
        """Refresh access token using secure storage."""
        creds = secure_storage.get_credentials()
        if not creds:
            raise Exception("Could not retrieve credentials from keychain")

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
            raise Exception(f"Token refresh failed: {response.text}")

        data = response.json()

        # Update tokens in secure storage
        secure_storage.update_tokens(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
        )

        # Update metadata
        self._metadata["expires_at"] = data["expires_at"]
        self._save_metadata()

    def _ensure_valid_token(self):
        """Ensure we have a valid access token."""
        if self._is_token_expired():
            self._refresh_token()

    def _get_access_token(self) -> str:
        """Get access token from secure storage."""
        creds = secure_storage.get_credentials()
        if not creds:
            raise Exception("Could not retrieve credentials from keychain")
        return creds["access_token"]

    def _headers(self) -> dict:
        """Get request headers with authorization."""
        return {"Authorization": f"Bearer {self._get_access_token()}"}

    @property
    def athlete_id(self) -> int | None:
        """Get athlete ID from metadata."""
        return self._metadata.get("athlete_id")

    def get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request."""
        self._ensure_valid_token()
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict = None, json_data: dict = None) -> dict:
        """Make POST request."""
        self._ensure_valid_token()
        url = f"{BASE_URL}{endpoint}"
        response = requests.post(
            url, headers=self._headers(), data=data, json=json_data
        )
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, data: dict = None, json_data: dict = None) -> dict:
        """Make PUT request."""
        self._ensure_valid_token()
        url = f"{BASE_URL}{endpoint}"
        response = requests.put(
            url, headers=self._headers(), data=data, json=json_data
        )
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str) -> bool:
        """Make DELETE request."""
        self._ensure_valid_token()
        url = f"{BASE_URL}{endpoint}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return response.status_code == 204

    # Convenience methods
    def get_athlete(self) -> dict:
        """Get authenticated athlete profile."""
        return self.get("/athlete")

    def get_athlete_stats(self, athlete_id: int = None) -> dict:
        """Get athlete statistics."""
        if athlete_id is None:
            athlete_id = self.athlete_id
        return self.get(f"/athletes/{athlete_id}/stats")

    def list_activities(
        self,
        before: int = None,
        after: int = None,
        page: int = 1,
        per_page: int = 30,
    ) -> list:
        """List athlete activities."""
        params = {"page": page, "per_page": per_page}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self.get("/athlete/activities", params)

    def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> dict:
        """Get activity details."""
        params = {"include_all_efforts": include_all_efforts}
        return self.get(f"/activities/{activity_id}", params)

    def create_activity(
        self,
        name: str,
        sport_type: str,
        start_date_local: str,
        elapsed_time: int,
        description: str = None,
        distance: float = None,
        trainer: bool = False,
        commute: bool = False,
    ) -> dict:
        """Create a manual activity."""
        data = {
            "name": name,
            "sport_type": sport_type,
            "start_date_local": start_date_local,
            "elapsed_time": elapsed_time,
            "trainer": trainer,
            "commute": commute,
        }
        if description:
            data["description"] = description
        if distance:
            data["distance"] = distance
        return self.post("/activities", data=data)

    def update_activity(self, activity_id: int, **kwargs) -> dict:
        """Update an activity."""
        return self.put(f"/activities/{activity_id}", data=kwargs)

    def get_activity_streams(
        self, activity_id: int, keys: list = None
    ) -> dict:
        """Get activity streams (detailed data)."""
        if keys is None:
            keys = ["time", "distance", "altitude", "heartrate", "velocity_smooth"]
        params = {"keys": ",".join(keys), "key_by_type": True}
        return self.get(f"/activities/{activity_id}/streams", params)

    def get_activity_laps(self, activity_id: int) -> list:
        """Get activity laps."""
        return self.get(f"/activities/{activity_id}/laps")

    def explore_segments(
        self,
        bounds: str,
        activity_type: str = "running",
        min_cat: int = None,
        max_cat: int = None,
    ) -> dict:
        """Explore segments in area. bounds format: SW_lat,SW_lng,NE_lat,NE_lng"""
        params = {"bounds": bounds, "activity_type": activity_type}
        if min_cat is not None:
            params["min_cat"] = min_cat
        if max_cat is not None:
            params["max_cat"] = max_cat
        return self.get("/segments/explore", params)

    def get_segment(self, segment_id: int) -> dict:
        """Get segment details."""
        return self.get(f"/segments/{segment_id}")

    def get_route(self, route_id: int) -> dict:
        """Get route details."""
        return self.get(f"/routes/{route_id}")

    def list_athlete_routes(self, athlete_id: int = None, page: int = 1, per_page: int = 30) -> list:
        """List athlete routes."""
        if athlete_id is None:
            athlete_id = self.athlete_id
        params = {"page": page, "per_page": per_page}
        return self.get(f"/athletes/{athlete_id}/routes", params)

    def get_gear(self, gear_id: str) -> dict:
        """Get gear details."""
        return self.get(f"/gear/{gear_id}")

    def list_clubs(self, page: int = 1, per_page: int = 30) -> list:
        """List athlete's clubs."""
        params = {"page": page, "per_page": per_page}
        return self.get("/athlete/clubs", params)

    def get_club(self, club_id: int) -> dict:
        """Get club details."""
        return self.get(f"/clubs/{club_id}")


def main():
    """CLI interface for common operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Strava API Client")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Athlete
    subparsers.add_parser("athlete", help="Get athlete profile")
    subparsers.add_parser("stats", help="Get athlete stats")

    # Activities
    list_parser = subparsers.add_parser("activities", help="List activities")
    list_parser.add_argument("--limit", "-n", type=int, default=10, help="Number of activities")

    get_parser = subparsers.add_parser("activity", help="Get activity details")
    get_parser.add_argument("id", type=int, help="Activity ID")

    # Segments
    explore_parser = subparsers.add_parser("segments", help="Explore segments")
    explore_parser.add_argument("bounds", help="SW_lat,SW_lng,NE_lat,NE_lng")
    explore_parser.add_argument("--type", default="running", help="running or riding")

    # Raw request
    raw_parser = subparsers.add_parser("raw", help="Make raw API request")
    raw_parser.add_argument("method", choices=["GET", "POST", "PUT", "DELETE"])
    raw_parser.add_argument("endpoint", help="API endpoint (e.g., /athlete)")
    raw_parser.add_argument("--data", help="JSON data for POST/PUT")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    client = StravaClient()

    try:
        if args.command == "athlete":
            result = client.get_athlete()
        elif args.command == "stats":
            result = client.get_athlete_stats()
        elif args.command == "activities":
            result = client.list_activities(per_page=args.limit)
        elif args.command == "activity":
            result = client.get_activity(args.id, include_all_efforts=True)
        elif args.command == "segments":
            result = client.explore_segments(args.bounds, args.type)
        elif args.command == "raw":
            if args.method == "GET":
                result = client.get(args.endpoint)
            elif args.method == "POST":
                data = json.loads(args.data) if args.data else None
                result = client.post(args.endpoint, json_data=data)
            elif args.method == "PUT":
                data = json.loads(args.data) if args.data else None
                result = client.put(args.endpoint, json_data=data)
            elif args.method == "DELETE":
                result = client.delete(args.endpoint)
        else:
            parser.print_help()
            return

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e.response.status_code}")
        print(e.response.text)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
