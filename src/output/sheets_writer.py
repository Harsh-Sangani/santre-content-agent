"""
Writes content package rows to a new tab in the tracking Google Sheet,
created fresh each week.

Columns: Day | Theme | Image Link | Caption | Status | Retry Count
"""

import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER_ROW = ["Day", "Theme", "Image Link", "Caption", "Status", "Retry Count"]


def _get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"], scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def create_week_tab(spreadsheet_id: str, tab_name: str) -> None:
    """Create a new tab with the header row, if it doesn't already exist."""
    service = _get_sheets_service()
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing_titles = [s["properties"]["title"] for s in sheet_metadata["sheets"]]

    if tab_name not in existing_titles:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
        ).execute()

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!A1",
            valueInputOption="RAW",
            body={"values": [HEADER_ROW]},
        ).execute()


def append_row(spreadsheet_id: str, tab_name: str, row: list[str]) -> None:
    """Append one content package row to the given week's tab."""
    service = _get_sheets_service()
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
