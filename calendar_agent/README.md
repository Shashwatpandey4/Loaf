# Google Calendar integration (calendar_agent)

Setup
 - Create OAuth credentials in Google Cloud Console (Application type: Desktop) and download the JSON.
 - Save the file in the repo root as `credentials.json` (or pass an explicit path to the CLI).
 - Install the helper requirements

Notes
 - The first run will open a browser window to authorize the app. A `token.json` file will be created to cache credentials.
 - This module provides `get_credentials`, `create_event`, and `create_event_from_details` to integrate with your agent code.

# Google Calendar integration (calendar_agent)

Setup
 - Create OAuth credentials in Google Cloud Console (Application type: Desktop) and download the JSON.
 - Save the file in the repo root as `credentials.json` (or pass an explicit path to the CLI).
 - Install dependencies from the project's main `requirements.txt` (calendar packages were merged there):

  pip install -r requirements.txt

Usage
 - Quick CLI demo (Windows cmd):

  python scripts\add_calendar_event.py --title "Meal prep: Chicken" --start "2025-11-21T18:00" --duration 90 --timezone "America/Los_Angeles"

