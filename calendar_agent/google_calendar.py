from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except Exception:
    raise ImportError(
        "Missing Google libraries. Install from `requirements-calendar.txt` or run: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`")

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def get_credentials(
    client_secrets_file: str = "credentials.json",
    token_file: str = "token.json",
    scopes: list[str] | None = None,
) -> Credentials:
    scopes = scopes or SCOPES
    creds: Optional[Credentials] = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(
                    f"Client secrets file not found at '{client_secrets_file}'. "
                    "Create OAuth credentials in Google Cloud and download the file as 'credentials.json'."
                )
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def create_event(
    credentials: Credentials,
    event_body: dict,
    calendar_id: str = "primary",
) -> dict:
    service = build("calendar", "v3", credentials=credentials)
    created = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    return created


def create_event_from_details(
    credentials: Credentials,
    title: str,
    start_dt: datetime,
    duration_minutes: int = 60,
    description: str = "",
    timezone: str = "UTC",
    calendar_id: str = "primary",
) -> dict:
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
    }

    return create_event(credentials, event, calendar_id=calendar_id)


if __name__ == "__main__":
    print("This module provides helpers to create Google Calendar events.")
