import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar']

def google_connections() -> tuple[Resource, Resource]:
    """
    Authenticate and build Google Calendar and Gmail services.
    :returns: Google Calendar & Gmail services.
    """
    creds = get_google_creds();

    try:
        print('Creating Gmail and Google calendar connections.');
        gmail_service = build('gmail', 'v1', credentials=creds)
        calendar_service = build('calendar', 'v3', credentials=creds)
        print('Connections created successfully!');
    except Exception as ex:
        print(f'Issue creating Gmail or Google Calendar connections: \n {ex}');

    return gmail_service, calendar_service;

def get_google_creds():
    """
    Get credentials to authenticate the client to access google services.
    :return: Google service credentials.
    """
    creds = None
    # Token file stores user access token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds;
