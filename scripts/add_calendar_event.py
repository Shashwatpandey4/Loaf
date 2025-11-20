"""Add a Google Calendar event for a meal prep item.
Before running: place your Google OAuth client secrets JSON at `credentials.json` in the repo root.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import os
import sys

from calendar_agent.google_calendar import get_credentials, create_event_from_details


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Add a Google Calendar event for a meal prep item")
    p.add_argument("--title", required=True, help="Event title")
    p.add_argument("--start", required=True, help="Start datetime in ISO format, e.g. 2025-11-21T18:00")
    p.add_argument("--duration", type=int, default=60, help="Duration in minutes (default: 60)")
    p.add_argument("--description", default="", help="Event description")
    p.add_argument("--credentials", default="credentials.json", help="Path to Google client secrets JSON")
    p.add_argument("--token", default="token.json", help="Path to store token JSON")
    p.add_argument("--timezone", default="UTC", help="IANA timezone for the event (default: UTC)")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        start_dt = datetime.fromisoformat(args.start)
    except Exception as e:
        print(f"Invalid start datetime: {e}")
        return 2

    creds = get_credentials(client_secrets_file=args.credentials, token_file=args.token)

    created = create_event_from_details(
        credentials=creds,
        title=args.title,
        start_dt=start_dt,
        duration_minutes=args.duration,
        description=args.description,
        timezone=args.timezone,
    )

    print("Event created:")
    print(created.get("htmlLink"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
