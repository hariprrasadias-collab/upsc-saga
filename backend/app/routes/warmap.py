from flask import Blueprint, request, jsonify, redirect, session, url_for
import os
import datetime
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

warmap = Blueprint('warmap', __name__)

# Configuration
CREDENTIALS_FILE = os.path.join(os.getcwd(), 'credentials.json')
TOKEN_FILE = os.path.join(os.getcwd(), 'token.json')
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
# Allow HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Relax scope validation as Google may return more scopes than requested (e.g. if user previously granted readonly)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
    
    return creds

@warmap.route('/api/warmap/status')
def google_status():
    creds = get_credentials()
    return jsonify({"connected": creds is not None and creds.valid})

@warmap.route('/api/warmap/google-auth')
def google_auth():
    if not os.path.exists(CREDENTIALS_FILE):
        return jsonify({"error": "credentials.json not found. Please configure Google Cloud credentials."}), 404

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('warmap.google_callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@warmap.route('/api/warmap/google-callback')
def google_callback():
    state = session.get('state')
    if not state or state != request.args.get('state'):
        return jsonify({"error": "Invalid state parameter"}), 400

    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=url_for('warmap.google_callback', _external=True)
        )
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        # Redirect back to frontend
        return redirect('http://localhost:5177/warmap?status=connected')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@warmap.route('/api/warmap/google-events')
def google_events():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authenticated"}), 401

    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date parameter required"}), 400

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Parse date and set time range for the entire day
        target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        time_min = target_date.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        time_max = target_date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary', 
            timeMin=time_min, 
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                'id': event['id'],
                'title': event['summary'],
                'start': start,
                'link': event.get('htmlLink'),
                'description': event.get('description'),
                'source': 'google_calendar'
            })

        return jsonify(formatted_events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_google_calendar_event(title, start_time, end_time, description=None):
    """
    Creates an event in the user's primary Google Calendar.
    start_time and end_time should be ISO format strings (e.g., '2023-10-27T10:00:00').
    """
    creds = get_credentials()
    if not creds:
        print("No credentials found for Google Calendar sync.")
        return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata', # Assuming IST based on user location
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
        return event
    except Exception as e:
        print(f"Error creating Google Calendar event: {e}")
        return None

# ============================================================================
# NEW ROUTES FOR GOOGLE CALENDAR EVENT MANAGEMENT
# ============================================================================

from app.db import get_db

@warmap.route('/api/warmap/google-events/<event_id>/complete', methods=['POST'])
def complete_google_event(event_id):
    """Mark a Google Calendar event as complete"""
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Get the event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Mark as complete (add to description)
        description = event.get('description', '')
        if '✓ Completed in UPSC Saga' not in description:
            event['description'] = description + '\n\n✓ Completed in UPSC Saga'
            
            # Update event
            service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
        
        # Get XP metadata and award XP
        conn = get_db()
        user_id = 1  # Get from session in production
        
        metadata = conn.execute('''
            SELECT xp_reward FROM calendar_event_metadata 
            WHERE event_id = ? AND user_id = ?
        ''', (event_id, user_id)).fetchone()
        
        xp_reward = metadata['xp_reward'] if metadata else 0
        
        # Award XP if it exists
        if xp_reward > 0:
            conn.execute('''
                UPDATE users
                SET current_xp = current_xp + ?
                WHERE id = ?
            ''', (xp_reward, user_id))
        
        # Update metadata to mark as completed
        conn.execute('''
            INSERT OR REPLACE INTO calendar_event_metadata 
            (event_id, user_id, xp_reward, is_completed)
            VALUES (?, ?, ?, 1)
        ''', (event_id, user_id, xp_reward))
        conn.commit()
        
        return jsonify({'success': True, 'xp_awarded': xp_reward})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warmap.route('/api/warmap/google-events/<event_id>/uncomplete', methods=['POST'])
def uncomplete_google_event(event_id):
    """Unmark a Google Calendar event as complete"""
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Remove completed marker from description
        description = event.get('description', '')
        description = description.replace('\n\n✓ Completed in UPSC Saga', '')
        event['description'] = description
        
        service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        # Update local DB
        conn = get_db()
        user_id = 1
        conn.execute('''
            INSERT OR REPLACE INTO calendar_event_metadata 
            (event_id, user_id, is_completed)
            VALUES (?, ?, 0)
        ''', (event_id, user_id))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warmap.route('/api/warmap/google-events/<event_id>', methods=['PUT'])
def update_google_event(event_id):
    """Update a Google Calendar event's times"""
    data = request.get_json()
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Get user timezone
        conn = get_db()
        user_tz = conn.execute('SELECT timezone FROM users WHERE id = 1').fetchone()
        timezone = user_tz['timezone'] if user_tz else 'Asia/Kolkata'
        
        # Update times if provided
        if 'start_time' in data:
            event['start'] = {
                'dateTime': data['start_time'],
                'timeZone': timezone
            }
        if 'end_time' in data:
            event['end'] = {
                'dateTime': data['end_time'],
                'timeZone': timezone
            }
        
        updated = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return jsonify({'success': True, 'event': updated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warmap.route('/api/warmap/google-events/<event_id>', methods=['DELETE'])
def delete_google_event(event_id):
    """Delete a Google Calendar event"""
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        # Also delete from local metadata
        conn = get_db()
        conn.execute('DELETE FROM calendar_event_metadata WHERE event_id = ?', (event_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warmap.route('/api/warmap/google-events/<event_id>/metadata', methods=['GET', 'PUT'])
def event_metadata(event_id):
    """Get or update XP metadata for a Google Calendar event"""
    conn = get_db()
    user_id = 1  # Get from session in production
    
    if request.method == 'GET':
        metadata = conn.execute('''
            SELECT * FROM calendar_event_metadata 
            WHERE event_id = ? AND user_id = ?
        ''', (event_id, user_id)).fetchone()
        
        if metadata:
            return jsonify(dict(metadata))
        else:
            return jsonify({'xp_reward': 0, 'associated_stat': None, 'is_completed': False})
    
    elif request.method == 'PUT':
        data = request.get_json()
        conn.execute('''
            INSERT OR REPLACE INTO calendar_event_metadata 
            (event_id, user_id, xp_reward, associated_stat, is_completed, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            event_id, 
            user_id, 
            data.get('xp_reward', 0),
            data.get('associated_stat'),
            data.get('is_completed', 0)
        ))
        conn.commit()
        
        return jsonify({'success': True})
