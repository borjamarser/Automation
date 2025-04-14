import os.path
import base64
import json
import datetime
from google_connections import google_connections
from google_calendar_helper import get_calendar_id, cal_event_already_exists, create_calendar_event
from googleapiclient.discovery import Resource

def check_football_email(service: Resource) -> tuple[str, datetime, str]:
    """
    Get football email with event information.
    :param service: Google Gmail service.
    :return: Event information - match, time, date and location.
    """
    today = datetime.datetime.utcnow().date()
    tomorrow = today + datetime.timedelta(days=1)

    football_email = "no-reply@portal.playfootball.net";
    query = f'after:{today.strftime("%Y/%m/%d")} before:{tomorrow.strftime("%Y/%m/%d")} from:{football_email}'

    try:
        print('Checking emails...')
        result = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=1
        ).execute()

        message = result.get('messages', [])[0];

        msg_data = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        event_info = subject.split(',');
        print(f"Found football email notification: {subject}")

        full_datetime_str = f'{event_info[2]}{event_info[1]} {datetime.datetime.now().year}'.strip();
        dt = datetime.datetime.strptime(full_datetime_str, '%A %d %B %H:%M %Y')
        return event_info[0], dt, event_info[3]
        #snippet = msg_data.get('snippet')

    except Exception as ex:
        print(f'Issue finding football email in time range: {today.strftime("%Y-%m-%d %H:%M:%S")} -'
              f'{tomorrow.strftime("%Y-%m-%d %H:%M:%S")} \n {ex}');
        exit()

def sync_event_to_calendar(service: Resource, event_name: str, event_datetime: datetime, event_location: str):
    """
    Add found event from email notifications to Google Calendar.
    :param service: Google Calendar service.
    :param event_name: Title of event to add.
    :param event_datetime: Datetime of event.
    :param event_location: Location of event.
    """
    calendar_id = get_calendar_id(service, 'Personal');

    if cal_event_already_exists(service, calendar_id, event_name, event_datetime):
        print('Exiting...')
        return
    else:
        create_calendar_event(service, calendar_id, event_name, event_datetime, event_location);

if __name__ == '__main__':
    print('Initiating football email - calendar sync...');
    gmail_service, calendar_service = google_connections();

    event_title, event_dt, event_loc = check_football_email(gmail_service);
    sync_event_to_calendar(calendar_service, event_title, event_dt, event_loc);
