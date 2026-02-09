# Google OAuth 2.0 Setup Guide

Complete walkthrough for setting up Google OAuth 2.0 Desktop credentials. This enables API access to **Google Calendar** and **Gmail** from local tools like MCP servers, scripts, and CLI agents.

This is the **canonical OAuth guide** for the calendar-mcp and gmail-mcp projects.

---

## Table of Contents

1. [Create a Google Cloud Project](#1-create-a-google-cloud-project)
2. [Enable APIs](#2-enable-apis)
3. [Configure OAuth Consent Screen](#3-configure-oauth-consent-screen)
4. [Add Test Users](#4-add-test-users)
5. [Create OAuth 2.0 Client ID](#5-create-oauth-20-client-id)
6. [Download credentials.json](#6-download-credentialsjson)
7. [Understand the Auth Flow](#7-understand-the-auth-flow)
8. [First Token Exchange](#8-first-token-exchange)
9. [Security Notes](#9-security-notes)
10. [Scopes Reference](#10-scopes-reference)

---

## 1. Create a Google Cloud Project

Go to the Google Cloud Console:

> **[Google Cloud - Create Project](https://console.cloud.google.com/projectcreate)**

- **Project name**: Something descriptive like `claude-agent` or `mcp-services`. This project will be shared across calendar-mcp, gmail-mcp, and any other Google API integrations.
- **Organization**: Leave as "No organization" if using a personal Gmail account.
- **Location**: Leave as default.

Click **Create**.

If you already have a project you want to reuse, select it from the project dropdown at the top of the Console. Just make sure you enable the required APIs (next step) in that project.

After creation, confirm you are working in the correct project by checking the project name in the top navigation bar.

---

## 2. Enable APIs

You need to enable two APIs in your project:

### Google Calendar API

1. Go to: **[Google Calendar API Library Page](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)**
2. Click **Enable**.

### Gmail API

1. Go to: **[Gmail API Library Page](https://console.cloud.google.com/apis/library/gmail.googleapis.com)**
2. Click **Enable**.

Alternatively, navigate manually:

1. Open the left sidebar menu (hamburger icon).
2. Go to **APIs & Services** > **Library**.
3. Search for "Google Calendar API", click the result, and click **Enable**.
4. Go back to the Library, search for "Gmail API", click the result, and click **Enable**.

You can verify both are enabled at:

> **[APIs & Services Dashboard](https://console.cloud.google.com/apis/dashboard)**

Both "Google Calendar API" and "Gmail API" should appear in the list of enabled APIs.

---

## 3. Configure OAuth Consent Screen

Navigate to:

> **[OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)**

If prompted to choose a user type:

- Select **External** (this works for personal Gmail accounts and allows you to add specific test users).
- Click **Create**.

Fill in the consent screen form:

### App Information

| Field | Value |
|-------|-------|
| **App name** | `Claude Agent` (or whatever you prefer -- users will see this during consent) |
| **User support email** | Select your email from the dropdown |

### App Domain

Leave all fields blank (App homepage, Privacy policy, Terms of service). These are optional and not needed for a Desktop app in test mode.

### Authorized Domains

Leave blank. Not needed for Desktop app credentials.

### Developer Contact Information

| Field | Value |
|-------|-------|
| **Email addresses** | Enter your email address |

Click **Save and Continue**.

### Scopes Screen

Click **Add or Remove Scopes**. In the filter, search for and add the following scopes:

| Scope | Description |
|-------|-------------|
| `https://www.googleapis.com/auth/calendar` | Full access to Google Calendar |
| `https://www.googleapis.com/auth/gmail.modify` | Read, compose, send, and modify Gmail (all except permanent delete) |

If you do not see them listed, type the full scope URL in the "Manually add scopes" text box at the bottom and click **Add to Table**.

Click **Update**, then **Save and Continue**.

### Test Users Screen

Skip this for now (we will add test users in the next step). Click **Save and Continue**.

### Summary

Review the summary and click **Back to Dashboard**.

---

## 4. Add Test Users

While your app is in "Testing" publishing status (the default), only explicitly listed test users can complete the OAuth flow. Anyone not on the list will see an error.

Navigate to:

> **[OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)**

Click **Edit App** if needed, then navigate to the **Test users** section (or the "OAuth consent screen" page and look for the "Test users" panel).

Alternatively, on the OAuth consent screen page, scroll down to the **Test users** section and click **Add Users**.

Add the following email addresses:

```
draneylucas@gmail.com
lucastoddraney@gmail.com
devopsphilosopher@gmail.com
```

Click **Save**.

**Important**: Test mode has a limit of 100 test users. Tokens issued in test mode expire after 7 days, so you will need to re-authenticate periodically (unless you publish the app, which requires verification).

---

## 5. Create OAuth 2.0 Client ID

Navigate to:

> **[Credentials Page](https://console.cloud.google.com/apis/credentials)**

Click **+ Create Credentials** at the top, then select **OAuth client ID**.

| Field | Value |
|-------|-------|
| **Application type** | **Desktop app** |
| **Name** | `calendar-mcp` (or any descriptive name) |

Click **Create**.

### Why "Desktop app"?

Desktop app credentials use a localhost redirect URI (`http://localhost:PORT`) for the OAuth callback. This means:

- No hosted web server or public URL is needed.
- The auth flow opens a browser on your local machine, you consent, and the browser redirects back to `localhost` where a temporary local server captures the authorization code.
- This is the correct choice for CLI tools, local scripts, and MCP servers running on your machine.

A dialog will appear showing your **Client ID** and **Client Secret**. You do not need to copy these manually -- download the JSON file instead (next step).

---

## 6. Download credentials.json

In the dialog that appeared after creating the client ID (or from the Credentials page by clicking the download icon next to your client):

1. Click **Download JSON**.
2. Save the file and move it to the canonical location:

```bash
# Create the directory
mkdir -p ~/secrets/google-oauth

# Move the downloaded file (adjust the source path to your Downloads folder)
mv ~/Downloads/client_secret_*.json ~/secrets/google-oauth/credentials.json

# Lock down permissions
chmod 700 ~/secrets/google-oauth
chmod 600 ~/secrets/google-oauth/credentials.json
```

The file will look something like this:

```json
{
  "installed": {
    "client_id": "123456789-abcdef.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-...",
    "redirect_uris": ["http://localhost"]
  }
}
```

Note the top-level key is `"installed"` -- this indicates Desktop app credentials (as opposed to `"web"` for web app credentials).

---

## 7. Understand the Auth Flow

Google OAuth 2.0 for Desktop apps uses the **Authorization Code Flow with a localhost redirect**. Here is how it works:

```
┌─────────┐         ┌─────────────┐         ┌──────────────┐
│  Your    │         │   Google    │         │   Google     │
│  Script  │         │   Auth      │         │   API        │
└────┬─────┘         └──────┬──────┘         └──────┬───────┘
     │                      │                       │
     │  1. Start local HTTP │                       │
     │     server on        │                       │
     │     localhost:PORT   │                       │
     │                      │                       │
     │  2. Open browser to  │                       │
     │     Google auth URL  │                       │
     │ ──────────────────>  │                       │
     │                      │                       │
     │     3. User consents │                       │
     │        in browser    │                       │
     │                      │                       │
     │  4. Google redirects │                       │
     │     to localhost     │                       │
     │     with auth code   │                       │
     │ <──────────────────  │                       │
     │                      │                       │
     │  5. Exchange auth    │                       │
     │     code for tokens  │                       │
     │ ──────────────────>  │                       │
     │                      │                       │
     │  6. Receive:         │                       │
     │     - access_token   │                       │
     │     - refresh_token  │                       │
     │ <──────────────────  │                       │
     │                      │                       │
     │  7. Use access_token │                       │
     │     to call APIs     │                       │
     │ ─────────────────────────────────────────>   │
     │                      │                       │
```

### Key concepts

- **Authorization code**: A one-time code returned after the user consents. Exchanged for tokens.
- **Access token**: Short-lived (1 hour). Used in API requests as a Bearer token.
- **Refresh token**: Long-lived. Used to get new access tokens without user interaction. This is the token you store.
- **Why you only do this once**: After the first auth flow, you store the refresh token. Your application uses it to silently obtain new access tokens whenever the old one expires. No browser interaction is needed again (unless the refresh token is revoked or expires in test mode after 7 days).

### Refresh token lifecycle

- Google only returns the refresh token on the **first** authorization, or when you explicitly request it with `access_type=offline` and `prompt=consent`.
- If you lose the refresh token, you must re-authorize (revoke access at [Google Account Permissions](https://myaccount.google.com/permissions), then run the auth flow again).
- In test mode, refresh tokens expire after **7 days**. Publish your app to get long-lived refresh tokens.

---

## 8. First Token Exchange

Use the provided helper script to complete the OAuth flow and obtain your refresh token.

### Prerequisites

Install the Google auth library:

```bash
pip install google-auth-oauthlib
```

### Run the script

```bash
python scripts/get-refresh-token.py
```

This will:

1. Read your `~/secrets/google-oauth/credentials.json` file.
2. Open your default browser to Google's consent page.
3. After you consent, capture the authorization code via localhost redirect.
4. Exchange the code for tokens.
5. Save the token file to `~/secrets/google-oauth/token.json` (chmod 600).

The script requests both Calendar and Gmail scopes in a single flow, so you only need to authorize once for both projects.

### What gets saved

The token file (`~/secrets/google-oauth/token.json`) contains:

```json
{
  "token": "ya29.a0AfH6SM...",
  "refresh_token": "1//0dx...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789-abcdef.apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "scopes": [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify"
  ],
  "expiry": "2024-01-01T12:00:00.000000Z"
}
```

The `refresh_token` field is what matters. The `token` (access token) will be refreshed automatically by the Google client libraries.

### Verify it worked

Quick test to list your next 5 calendar events:

```bash
python -c "
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json, os

token_path = os.path.expanduser('~/secrets/google-oauth/token.json')
with open(token_path) as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('calendar', 'v3', credentials=creds)

from datetime import datetime, timezone
now = datetime.now(timezone.utc).isoformat()
events = service.events().list(calendarId='primary', timeMin=now, maxResults=5, singleEvents=True, orderBy='startTime').execute()

for event in events.get('items', []):
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(f'{start}: {event[\"summary\"]}')
"
```

If you see your upcoming events, everything is working.

---

## 9. Security Notes

### What to NEVER commit

The following files contain secrets and must **never** be checked into version control:

- `credentials.json` -- contains your client ID and client secret
- `token.json` -- contains your access token and refresh token
- Any `.env` file with OAuth values

### .gitignore patterns

Every project using these credentials should include these patterns in `.gitignore`:

```gitignore
# Google OAuth secrets
credentials.json
token.json
client_secret_*.json

# Environment files
.env
.env.*

# Python
__pycache__/
*.pyc
```

### File permissions

```bash
# Directory
chmod 700 ~/secrets/google-oauth/

# Credential files
chmod 600 ~/secrets/google-oauth/credentials.json
chmod 600 ~/secrets/google-oauth/token.json
```

### Centralized credential storage

This project stores credentials in `~/secrets/google-oauth/` rather than inside the project directory. This keeps secrets out of the repo entirely and allows multiple projects (calendar-mcp, gmail-mcp) to share the same credentials.

The `~/secrets/` directory is a private Git repo for personal secret management. Never push it to a public remote.

### Token revocation

If you believe your tokens have been compromised:

1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find your app name (e.g., "Claude Agent") and click **Remove Access**.
3. Delete `~/secrets/google-oauth/token.json`.
4. Re-run the auth flow with `scripts/get-refresh-token.py`.

---

## 10. Scopes Reference

### Calendar scopes

| Scope | Access Level | Used By |
|-------|-------------|---------|
| `https://www.googleapis.com/auth/calendar` | Full read/write access to Calendar | calendar-mcp |
| `https://www.googleapis.com/auth/calendar.readonly` | Read-only access to Calendar | Not used (we need write) |
| `https://www.googleapis.com/auth/calendar.events` | Read/write access to events only | Not used (calendar scope covers this) |

### Gmail scopes

| Scope | Access Level | Used By |
|-------|-------------|---------|
| `https://www.googleapis.com/auth/gmail.modify` | Read, compose, send, and modify (no permanent delete) | gmail-mcp |
| `https://www.googleapis.com/auth/gmail.readonly` | Read-only access to Gmail | Not used (we need send/modify) |
| `https://www.googleapis.com/auth/gmail.send` | Send only | Not used (modify covers this) |
| `https://www.googleapis.com/auth/gmail.compose` | Compose and send | Not used (modify covers this) |

### Why these specific scopes?

- **`calendar`** (full access): The calendar-mcp server needs to create, read, update, and delete events. The full `calendar` scope is the simplest way to enable all CRUD operations.
- **`gmail.modify`**: The gmail-mcp server needs to read mail, compose drafts, send messages, and modify labels/read status. The `gmail.modify` scope covers all of these without granting permanent delete permission, which is the principle of least privilege for our use case.

### Requesting both at once

The `get-refresh-token.py` script requests both scopes in a single authorization flow. The user only needs to consent once, and the resulting token works for both Calendar and Gmail API calls.

If you later need to add more scopes, you must re-authorize: delete `token.json`, add the new scope to the script, and run it again. Google does not support incremental scope addition for Desktop app credentials through the standard library flow.
