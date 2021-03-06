import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import mimetypes
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def getService():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        print("pickle failed")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def makeMessage(sender, recipients, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = recipients
    message['from'] = sender
    message['subject'] = subject
    print(message.as_string())
    print(type(str.encode(message.as_string())))
    return {'raw': base64.urlsafe_b64encode(str.encode(message.as_string())).decode(encoding="ascii")}

def sendMessage(service, user_id, message):
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    return message
