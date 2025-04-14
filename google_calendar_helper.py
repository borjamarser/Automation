from googleapiclient.discovery import Resource
import datetime

def get_calendar_id(service: Resource, calendar_name: str) -> str:
    """
    Get calendar ID of personal calendar.
    :param service: Google Calendar service.
    :param calendar_name: Target calendar name.
    :return: Calendar ID.
    """
    calendar_list = service.calendarList().list().execute()

    for calendar in calendar_list['items']:
        if calendar_name.lower() in calendar['summary'].lower():
            return calendar['id']

    return None

def cal_event_already_exists(service: Resource, calendar_id: str, event_name: str, event_datetime: datetime) -> bool:
    """
    Check if this event already exists in the calendar.
    :param service: Google Calendar service.
    :param calendar_id: Target calendar ID.
    :param event_name: Name of event - game this week.
    :param event_datetime: Datetime of event.
    :return: True if event already exists, false if not.
    """
    print('Checking if this event has already been created in the calendar...');
    time_min = datetime.datetime.combine(event_datetime, datetime.datetime.min.time()).isoformat() + 'Z'
    time_max = datetime.datetime.combine(event_datetime + datetime.timedelta(days=1),
                                         datetime.datetime.min.time()).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
        q=event_name
    ).execute()

    events = events_result.get("items", [])

    for event in events:
        if event.get("summary", "").strip().lower() == event_name.strip().lower():
            print(f"Calendar event with name '{event_name}' at datetime '{event_datetime.strftime('%Y-%m-%d %H:%M')}' "
                  f"already exists!");
            return True

    return False

def create_calendar_event(service: Resource, calendar_id: str, event_name: str,
                          event_datetime: datetime, event_location: str):
    """
    Create a Google Calendar event for the found event.
    :param service: Google Gmail service.
    :param calendar_id: ID of target calendar to add event into.
    :param event_name: Title of event/match.
    :param event_datetime: Datetime of event.
    :param event_location: Location of event.
    """
    try:
        cal_event = {
            'summary': event_name,
            'location': event_location,
            #'description': 'Discuss project scope, timeline, and deliverables.',
            'start': {
                'dateTime': event_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Europe/London',
            },
            'end': {
                'dateTime': (event_datetime + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Europe/London',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 4 * 60}
                ]
            }
        }

        created_event = service.events().insert(calendarId=calendar_id, body=cal_event).execute()

        print(f"✅ Event created: {created_event.get('htmlLink')}")

    except Exception as ex:
        print(f'Issue creating calendar event: \n {ex}');