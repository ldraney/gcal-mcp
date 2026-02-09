#!/usr/bin/env python3
"""
Google OAuth 2.0 token exchange for Desktop app credentials.

This script performs the one-time OAuth flow to obtain a refresh token
for Google Calendar API and Gmail API access.

Prerequisites:
    pip install google-auth-oauthlib

Usage:
    python scripts/get-refresh-token.py

    Optional flags:
        --credentials PATH   Path to credentials.json
                             (default: ~/secrets/google-oauth/credentials.json)
        --token PATH         Path to save token.json
                             (default: ~/secrets/google-oauth/token.json)
        --port PORT          Localhost port for OAuth redirect
                             (default: 8080)

See docs/google-oauth-setup.md for the full setup guide.
"""

import argparse
import json
import os
import stat
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Error: google-auth-oauthlib is not installed.")
    print("Install it with: pip install google-auth-oauthlib")
    sys.exit(1)

# Scopes for both Calendar and Gmail access.
# Requesting both in one flow so the user only authorizes once.
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
]

DEFAULT_CREDENTIALS_PATH = os.path.expanduser(
    "~/secrets/google-oauth/credentials.json"
)
DEFAULT_TOKEN_PATH = os.path.expanduser("~/secrets/google-oauth/token.json")
DEFAULT_PORT = 8080


def parse_args():
    parser = argparse.ArgumentParser(
        description="Obtain Google OAuth 2.0 refresh token for Calendar and Gmail APIs."
    )
    parser.add_argument(
        "--credentials",
        default=DEFAULT_CREDENTIALS_PATH,
        help=f"Path to credentials.json (default: {DEFAULT_CREDENTIALS_PATH})",
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN_PATH,
        help=f"Path to save token.json (default: {DEFAULT_TOKEN_PATH})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Localhost port for OAuth redirect (default: {DEFAULT_PORT})",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    credentials_path = os.path.expanduser(args.credentials)
    token_path = os.path.expanduser(args.token)

    # --- Validate credentials file exists ---
    if not os.path.isfile(credentials_path):
        print(f"Error: Credentials file not found at: {credentials_path}")
        print()
        print("Download it from the Google Cloud Console:")
        print("  https://console.cloud.google.com/apis/credentials")
        print()
        print("See docs/google-oauth-setup.md for full instructions.")
        sys.exit(1)

    # --- Ensure output directory exists ---
    token_dir = os.path.dirname(token_path)
    if token_dir:
        os.makedirs(token_dir, mode=0o700, exist_ok=True)

    # --- Check for existing token ---
    if os.path.isfile(token_path):
        print(f"Token file already exists at: {token_path}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("Aborted.")
            sys.exit(0)

    # --- Run the OAuth flow ---
    print()
    print("Starting OAuth flow...")
    print(f"  Credentials: {credentials_path}")
    print(f"  Scopes:      {', '.join(SCOPES)}")
    print(f"  Redirect:    http://localhost:{args.port}")
    print()
    print("A browser window will open. Sign in and grant access.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        scopes=SCOPES,
    )

    # run_local_server handles the full flow:
    #   1. Starts a local HTTP server on the specified port
    #   2. Opens the browser to Google's consent page
    #   3. Receives the redirect with the authorization code
    #   4. Exchanges the code for tokens
    credentials = flow.run_local_server(
        port=args.port,
        access_type="offline",
        prompt="consent",  # Force consent to ensure we get a refresh token
    )

    # --- Verify we got a refresh token ---
    if not credentials.refresh_token:
        print("Warning: No refresh token received.")
        print("This can happen if you previously authorized this app.")
        print("To fix: revoke access at https://myaccount.google.com/permissions")
        print("Then run this script again.")
        sys.exit(1)

    # --- Save token to disk ---
    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes),
    }

    if credentials.expiry:
        token_data["expiry"] = credentials.expiry.isoformat() + "Z"

    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)

    # Set restrictive permissions (owner read/write only)
    os.chmod(token_path, stat.S_IRUSR | stat.S_IWUSR)  # 600

    print()
    print(f"Token saved to: {token_path}")
    print(f"  Permissions: 600 (owner read/write only)")
    print()
    print("Scopes authorized:")
    for scope in credentials.scopes:
        print(f"  - {scope}")
    print()
    print("Refresh token obtained. You should not need to run this again")
    print("unless the token is revoked or expires (7 days in test mode).")


if __name__ == "__main__":
    main()
