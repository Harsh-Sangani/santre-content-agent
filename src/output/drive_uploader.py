"""
Uploads generated images to a per-week Google Drive folder and returns
shareable links.

Uses OAuth (acting as your personal Google account) rather than a service
account -- service accounts have no storage quota on regular Drive and
cannot create files there. Run scripts/generate_drive_token.py once locally
to generate token.json before using this.
"""

import io
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_FILE = os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", "token.json")


def _get_credentials() -> Credentials:
    with open(TOKEN_FILE, "r") as f:
        token_data = json.load(f)

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def _get_drive_service():
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds)


def get_or_create_week_folder(week_label: str, parent_folder_id: str) -> str: