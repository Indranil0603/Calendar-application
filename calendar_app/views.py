from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import Activity
from .forms import ActivityForm
from datetime import datetime, timezone, date
import json
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

# Helper function to get the start of the current month
def get_start_of_month():
    now = datetime.now(timezone.utc)  # Get current time in UTC
    start_of_month = datetime(now.year, now.month, 1, 0, 0, 0, 0, timezone.utc)
    return start_of_month.isoformat()

# Fetch events from Google Calendar
def fetch_google_calendar_events():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = settings.GOOGLE_SERVICE_ACCOUNT_FILE

    # Set up Google Calendar API credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the service object
    service = build('calendar', 'v3', credentials=credentials)
    
    now = datetime.utcnow().isoformat() + 'Z'
    # Fetch events from the start of the month
    events_result = service.events().list(calendarId='indranilsen1983@gmail.com', timeMin=get_start_of_month(),
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    
    events = events_result.get('items', [])

    # Process events into a dictionary
    event_dict = {}
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_date = datetime.fromisoformat(start).strftime('%Y-%m-%d')
        if start_date not in event_dict:
            event_dict[start_date] = []
        event_dict[start_date].append({
            'title': event.get('summary', 'No Title'),
            'description': event.get('description', '')
        })

    return event_dict

# Render the calendar view
def calendar_view(request):
    activity_dict = {}
    form = ActivityForm()
    google_events = fetch_google_calendar_events()
    
    # Combine Google Calendar events with activities
    for date, events in google_events.items():
        if date in activity_dict:
            activity_dict[date].extend(events)
        else:
            activity_dict[date] = events

    return render(request, 'calendar_app/calendar.html', {
        'activity_dict': json.dumps(activity_dict),
        'event_dates': list(google_events.keys()),
        'form': form
    })

# Handle the addition of a new activity
def add_activity(request, today=None):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save()

            # Create an event in Google Calendar
            event = {
                'summary': activity.title,
                'description': activity.description,
                'start': {
                    'date': activity.date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC',
                },
                'end': {
                    'date': activity.date.strftime('%Y-%m-%d'),
                    'timeZone': 'UTC',
                },
            }

            try:
                credentials = Credentials.from_service_account_file(
                    settings.GOOGLE_SERVICE_ACCOUNT_FILE,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )

                service = build('calendar', 'v3', credentials=credentials)
                calendar_id = 'indranilsen1983@gmail.com'
                event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
                logger.info(f"Event created: {event_result.get('htmlLink')}")
                print(event_result)
                return JsonResponse({
                    'success': True,
                    'activity': {
                        'title': activity.title,
                        'description': activity.description,
                        'date': activity.date.strftime('%Y-%m-%d')
                    }
                })
            except Exception as e:
                logger.error(f"Error creating event: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f"Error creating event: {str(e)}"
                })

        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        today = today or date.today()
        form = ActivityForm(initial={'date': today})
    return render(request, 'calendar_app/add_activity.html', {'form': form})

