from __future__ import print_function
import os.path
import pickle
from datetime import datetime, timedelta, timezone
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarNotifier:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate and create Google Calendar service."""
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('calendar', 'v3', credentials=self.creds)

    def parse_iso_datetime(self, iso_string):
        """Parse ISO 8601 string to datetime, fixing any formatting issues."""
        try:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        except ValueError:
            print(f"Invalid ISO format string: {iso_string}")
            return None

    def check_existing_event(self, event_name, onsale_datetime):
        """Check if an event already exists."""
        now = datetime.now(timezone.utc).isoformat()
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        for event in events:
            if event['summary'] == event_name and event['start']['dateTime'] == onsale_datetime.isoformat():
                return True
        return False

    def add_event(self, event_name, onsale_time, presale_time, location, event_date):
        """Add an event to Google Calendar."""
        onsale_datetime = self.parse_iso_datetime(onsale_time)
        presale_datetime = self.parse_iso_datetime(presale_time) if presale_time != 'No presale' else None
        event_datetime = self.parse_iso_datetime(event_date)

        if onsale_datetime is None or (event_datetime and event_datetime <= datetime.now(timezone.utc)):
            print(f"Skipping event {event_name} due to invalid or past date.")
            return

        if self.check_existing_event(event_name, onsale_datetime):
            print(f"Event '{event_name}' already exists.")
            return

        # Add event name with presale time if it's in the future
        if presale_datetime and presale_datetime > datetime.now(timezone.utc):
            self._create_event(event_name + " - Presale", presale_datetime, location, "Presale Time")

        # Add onsale time if it's in the future
        if onsale_datetime > datetime.now(timezone.utc):
            self._create_event(event_name + " - Onsale", onsale_datetime, location, "Onsale Time")

        # Add the event data if the event date itself is in the future
        if event_datetime and event_datetime > datetime.now(timezone.utc):
            self._create_event(event_name, event_datetime, location, f"Event Date: {event_date}")

    def _create_event(self, summary, start_time, location, description):
        """Helper method to create an event."""
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (start_time + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'description': f'{description}. Location: {location}',
        }

        # Insert the event into the primary calendar
        event_result = self.service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")

    def delete_all_events(self):
        """Delete all events from the calendar."""
        now = datetime.now(timezone.utc).isoformat()
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        for event in events:
            event_id = event['id']
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Event deleted: {event_id}")

if __name__ == '__main__':
    # Instantiate the GoogleCalendarNotifier class
    calendar_notifier = GoogleCalendarNotifier(credentials_file='path_to_credentials.json')
    
    # Call the delete_all_events method to delete all events
    calendar_notifier.delete_all_events()
