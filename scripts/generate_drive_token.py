"""
Run this ONCE locally to authenticate as yourself and generate token.json.

This opens a browser window, you log in with your personal Google account,
and it saves a reusable token (with refresh token) to token.json -- which
drive_uploader.py then uses for all future runs, including in GitHub Actions.

Usage:
    python scripts/generate_drive_token.py
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"Saved token to {TOKEN_FILE}. You can now run the pipeline normally.")


if __name__ == "__main__":
    main()