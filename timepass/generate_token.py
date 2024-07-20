import os
import django
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from django.conf import settings
import datetime
from googleapiclient.discovery import build

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timepass.settings')
django.setup()

# Scopes required for accessing Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events.readonly', 'https://www.googleapis.com/auth/calendar.events']
all_events = []
def main():
    creds = None

    # Check if token file exists
    if os.path.exists(settings.GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            settings.GOOGLE_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        def refresh_credentials():
            creds.refresh(Request())

        if creds and creds.expired and creds.refresh_token:
            refresh_credentials()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8000)

        # Save the credentials for the next run
        with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)
        now = f'{datetime.datetime.now(datetime.timezone.utc).isoformat()}Z'
        events = service.events().list(calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute()
        all_events.append(events)
        print(all_events)
if __name__ == '__main__':
    main()
