"""
Uploads generated images to a per-week Google Drive folder and returns
shareable links.

TODO: requires a Google service account with Drive API access, and the
service account email shared on the parent Drive folder (GOOGLE_DRIVE_PARENT_FOLDER_ID).
"""

import io
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"], scopes=SCOPES
    )
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
