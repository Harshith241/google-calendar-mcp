import os
import sys
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = '/app/credentials/token.pickle'
CREDENTIALS_FILE = '/app/credentials/credentials.json'

def authenticate():
    """Run OAuth flow to authenticate with Google Calendar."""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("ERROR: credentials.json not found!")
                print(f"Please place your OAuth credentials file at: {CREDENTIALS_FILE}")
                sys.exit(1)
            
            print("Starting OAuth flow...")
            print("A browser window will open. Please authorize the application.")
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
            
            print("Authentication successful!")
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            print(f"Credentials saved to {TOKEN_FILE}")
    else:
        print("Already authenticated!")
    
    return creds

if __name__ == '__main__':
    authenticate()
