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
    """Find or create a folder named e.g. 'Week_2026-06-28' under the parent folder."""
    service = _get_drive_service()
    query = (
        f"name='{week_label}' and '{parent_folder_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": week_label,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_image(image_bytes: bytes, filename: str, folder_id: str) -> str:
    """Upload image bytes to the given Drive folder, return a shareable link."""
    service = _get_drive_service()
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype="image/png")
    file_metadata = {"name": filename, "parents": [folder_id]}
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    service.permissions().create(
        fileId=file["id"], body={"role": "reader", "type": "anyone"}
    ).execute()

    return f"https://drive.google.com/file/d/{file['id']}/view"