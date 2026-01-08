import os
import sys
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from dateutil import parser
import pytz

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = '/app/credentials/token.pickle'
CREDENTIALS_FILE = '/app/credentials/credentials.json'

mcp = FastMCP("Google Calendar")

def get_calendar_service():
    """Authenticate and return Google Calendar service."""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                return None
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

@mcp.tool()
def check_availability(start_date: str = "", end_date: str = "", working_hours_only: str = "true"):
    """Check calendar availability between two dates. Dates should be in YYYY-MM-DD format."""
    try:
        service = get_calendar_service()
        if not service:
            return "Error: Calendar service not authenticated. Please run auth_setup.py first."
        
        if not start_date:
            start_dt = datetime.now()
        else:
            start_dt = parser.parse(start_date)
        
        if not end_date:
            end_dt = start_dt + timedelta(days=7)
        else:
            end_dt = parser.parse(end_date)
        
        time_min = start_dt.isoformat() + 'Z'
        time_max = end_dt.isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        result = f"Calendar Availability from {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}:\n\n"
        
        if not events:
            result += "No events scheduled. Fully available during this period."
            return result
        
        result += f"Found {len(events)} scheduled events:\n\n"
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'No title')
            
            start_time = parser.parse(start)
            end_time = parser.parse(end)
            
            result += f"- {summary}\n"
            result += f"  {start_time.strftime('%Y-%m-%d %I:%M %p')} - {end_time.strftime('%I:%M %p')}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return f"Error checking availability: {str(e)}"

@mcp.tool()
def schedule_meeting(title: str, start_datetime: str, duration_minutes: str = "30", attendees: str = "", description: str = "", add_meet_link: str = "true"):
    """Schedule a new meeting. start_datetime format: YYYY-MM-DD HH:MM. attendees: comma-separated emails."""
    try:
        service = get_calendar_service()
        if not service:
            return "Error: Calendar service not authenticated. Please run auth_setup.py first."
        
        start_dt = parser.parse(start_datetime)
        duration = int(duration_minutes)
        end_dt = start_dt + timedelta(minutes=duration)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        if attendees:
            attendee_list = [{'email': email.strip()} for email in attendees.split(',')]
            event['attendees'] = attendee_list
        
        if add_meet_link.lower() == "true":
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"meet-{datetime.now().timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1 if add_meet_link.lower() == "true" else 0,
            sendUpdates='all'
        ).execute()
        
        result = f"Meeting scheduled successfully!\n\n"
        result += f"Title: {title}\n"
        result += f"Start: {start_dt.strftime('%Y-%m-%d %I:%M %p')}\n"
        result += f"End: {end_dt.strftime('%Y-%m-%d %I:%M %p')}\n"
        result += f"Duration: {duration} minutes\n"
        
        if attendees:
            result += f"Attendees: {attendees}\n"
        
        if add_meet_link.lower() == "true" and 'conferenceData' in created_event:
            meet_link = created_event['conferenceData'].get('entryPoints', [{}])[0].get('uri', 'Not generated')
            result += f"Google Meet Link: {meet_link}\n"
        
        result += f"\nEvent ID: {created_event['id']}\n"
        result += f"View in Calendar: {created_event.get('htmlLink', 'N/A')}"
        
        return result
        
    except Exception as e:
        logger.error(f"Error scheduling meeting: {e}")
        return f"Error scheduling meeting: {str(e)}"

@mcp.tool()
def list_upcoming_events(max_results: str = "10", days_ahead: str = "7"):
    """List upcoming calendar events."""
    try:
        service = get_calendar_service()
        if not service:
            return "Error: Calendar service not authenticated. Please run auth_setup.py first."
        
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=int(days_ahead))).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=int(max_results),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No upcoming events in the next {days_ahead} days."
        
        result = f"Upcoming Events (next {days_ahead} days):\n\n"
        
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            event_id = event['id']
            
            start_time = parser.parse(start)
            result += f"{i}. {summary}\n"
            result += f"   Time: {start_time.strftime('%Y-%m-%d %I:%M %p')}\n"
            result += f"   Event ID: {event_id}\n"
            
            if 'conferenceData' in event:
                meet_link = event['conferenceData'].get('entryPoints', [{}])[0].get('uri')
                if meet_link:
                    result += f"   Meet Link: {meet_link}\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return f"Error listing events: {str(e)}"

@mcp.tool()
def reschedule_meeting(event_id: str, new_start_datetime: str, new_duration_minutes: str = "30"):
    """Reschedule an existing meeting to a new time. new_start_datetime format: YYYY-MM-DD HH:MM."""
    try:
        service = get_calendar_service()
        if not service:
            return "Error: Calendar service not authenticated. Please run auth_setup.py first."
        
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        new_start = parser.parse(new_start_datetime)
        new_duration = int(new_duration_minutes)
        new_end = new_start + timedelta(minutes=new_duration)
        
        event['start']['dateTime'] = new_start.isoformat()
        event['end']['dateTime'] = new_end.isoformat()
        
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        result = f"Meeting rescheduled successfully!\n\n"
        result += f"Title: {updated_event.get('summary', 'N/A')}\n"
        result += f"New Start: {new_start.strftime('%Y-%m-%d %I:%M %p')}\n"
        result += f"New End: {new_end.strftime('%Y-%m-%d %I:%M %p')}\n"
        result += f"Duration: {new_duration} minutes\n"
        result += f"\nView in Calendar: {updated_event.get('htmlLink', 'N/A')}"
        
        return result
        
    except HttpError as e:
        if e.resp.status == 404:
            return f"Error: Event with ID '{event_id}' not found."
        logger.error(f"Error rescheduling meeting: {e}")
        return f"Error rescheduling meeting: {str(e)}"
    except Exception as e:
        logger.error(f"Error rescheduling meeting: {e}")
        return f"Error rescheduling meeting: {str(e)}"

@mcp.tool()
def cancel_meeting(event_id: str, send_cancellation: str = "true"):
    """Cancel a meeting and optionally notify attendees."""
    try:
        service = get_calendar_service()
        if not service:
            return "Error: Calendar service not authenticated. Please run auth_setup.py first."
        
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        event_title = event.get('summary', 'Untitled Event')
        event_start = event['start'].get('dateTime', event['start'].get('date'))
        
        send_updates = 'all' if send_cancellation.lower() == "true" else 'none'
        
        service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates=send_updates
        ).execute()
        
        result = f"Meeting cancelled successfully!\n\n"
        result += f"Cancelled Event: {event_title}\n"
        result += f"Was scheduled for: {parser.parse(event_start).strftime('%Y-%m-%d %I:%M %p')}\n"
        
        if send_cancellation.lower() == "true":
            result += "\nCancellation notifications sent to all attendees."
        else:
            result += "\nNo notifications sent."
        
        return result
        
    except HttpError as e:
        if e.resp.status == 404:
            return f"Error: Event with ID '{event_id}' not found."
        logger.error(f"Error cancelling meeting: {e}")
        return f"Error cancelling meeting: {str(e)}"
    except Exception as e:
        logger.error(f"Error cancelling meeting: {e}")
        return f"Error cancelling meeting: {str(e)}"

@mcp.tool()
def find_free_slots(date: str = "", duration_minutes: str = "30", working_hours_only: str = "true"):
    """Find available time slots on a specific date. date format: YYYY-MM-DD."""
    try:
        service = get_calendar_service()
        if not service:
            return "Error: Calendar service not authenticated. Please run auth_setup.py first."
        
        if not date:
            target_date = datetime.now().date()
        else:
            target_date = parser.parse(date).date()
        
        duration = int(duration_minutes)
        
        start_hour = 9 if working_hours_only.lower() == "true" else 0
        end_hour = 18 if working_hours_only.lower() == "true" else 24
        
        day_start = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
        day_end = datetime.combine(target_date, datetime.min.time().replace(hour=end_hour))
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        busy_times = []
        for event in events:
            start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
            end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))
            busy_times.append((start, end))
        
        free_slots = []
        current_time = day_start
        
        for busy_start, busy_end in sorted(busy_times):
            if current_time + timedelta(minutes=duration) <= busy_start:
                free_slots.append((current_time, busy_start))
            current_time = max(current_time, busy_end)
        
        if current_time + timedelta(minutes=duration) <= day_end:
            free_slots.append((current_time, day_end))
        
        result = f"Available time slots for {target_date.strftime('%Y-%m-%d')}:\n"
        result += f"(Minimum duration: {duration} minutes)\n\n"
        
        if not free_slots:
            result += "No available slots found for the specified duration."
            return result
        
        for i, slot in enumerate(free_slots, 1):
            slot_start, slot_end = slot
            slot_duration = int((slot_end - slot_start).total_seconds() / 60)
            result += f"{i}. {slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')} ({slot_duration} minutes available)\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding free slots: {e}")
        return f"Error finding free slots: {str(e)}"

if __name__ == "__main__":
    mcp.run()
