import os
import pickle
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    if os.path.exists('confidential/token.pickle'):
        with open('confidential/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'confidential/credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('confidential/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_message(sender, to, subject, body, is_html=False):
    if is_html:
        message = MIMEText(body, "html")
    else:
        message = MIMEText(body)

    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw_message.decode()}

def send_message(service, user_id, message):
    return service.users().messages().send(userId=user_id, body=message).execute()
