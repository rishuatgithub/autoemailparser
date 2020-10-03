import read_config
import get_logger
import smtplib
import time
import imaplib
import email
import sys
import pickle
import os.path
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def decode_base64(data): 
    '''
        Decode Base64 data
    '''
    print(len(data), len(data)%4)

    if len(data)%4 == 0 and data[-1] != data[-2] and data[-1] == '=':
        data += data + '==='
    else: 
        data += '=' * (-len(data) % 4)
    return base64.b64decode(data)


def connect_to_gmail_server_unsecured(): 
    '''
        Try connecting to the email server
    '''
    mail = imaplib.IMAP4_SSL(config['EMAIL']['GMAIL']['GMAIL-UNSECURED']['SMTP_SERVER'])
    mail.login(account,account_pass)
    mail.select(config['EMAIL']['GMAIL']['GMAIL-UNSECURED']['DEFAULT_FOLDER'])

    type, data = mail.search(None, 'ALL')
    mail_ids = data[0]
    id_list = mail_ids.split()
    latest_email_id = int(id_list[-1])

    typ, data = mail.fetch(latest_email_id, '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1])
            email_subject = msg['subject']
            email_from = msg['from']
            print("EMAIL FROM: {}".format(email_from))
            print("EMAIL SUBJECT: {}".format(email_subject))


def connect_to_gmail_server_secured(credentials=None):
    '''
        Use GMAIL API (OAuth2) to connect to gmail inbox using credentials and pickle
        - copyright: https://developers.google.com/gmail/api/quickstart/python
    '''
    log.info("Trying to authenticate the Google email using the Google API")

    SCOPES=config['EMAIL']['GMAIL']['GMAIL-SECURED']['SCOPES']
    TOKEN_PATH=config['EMAIL']['GMAIL']['GMAIL-SECURED']['OAUTH_PIC_LOCATION']
    TOKEN_FILE=TOKEN_PATH+'token.pickle'
    creds = None

    if credentials == None: 
        api_credentials=config['EMAIL']['GMAIL']['GMAIL-SECURED']['CREDENTIAL_LOCATION']+'credentials.json'
    else:
        api_credentials=credentials

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(api_credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    log.info("Gmail authenticated and connected.")
    return service



def read_gmail_contents(folder=None): 
    '''
        This is for reading the email contents.
    '''
    log.info("Starting reading email content from the specified folders")

    service=connect_to_gmail_server_secured()

    if folder != None:
        gmail_folder_to_read = folder.upper()
    else: 
        gmail_folder_to_read = config['EMAIL']['GMAIL']['GMAIL-SECURED']['DEFAULT_FOLDER']
    
    # Call the Gmail API
    log.info("Calling the GMAIL API")
    results=service.users().threads().list(userId='me').execute()
    #results = service.users().labels().list(userId='me').execute()
    threads = results.get('threads', [])

    #log.info(threads)
    mail_contents=[]
    for thread in threads:
        tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
        msg = tdata['messages']
        
        contents = {}
        contents['id'] = msg[0]['id']
        contents['threadId']=msg[0]['threadId']
        contents['labelIds']=msg[0]['labelIds']

        ## this is for parsing the header content
        for header in msg[0]['payload']['headers']:
            if header['name'] == 'Subject':
                contents['Subject'] = header['value']

            if header['name'] == 'Delivered-To':
                contents['Delivered-To'] = header['value']

            if header['name'] == 'From':
                contents['From'] = header['value']
            
            if header['name'] == 'Date':
                contents['Date'] = header['value']

        ## this is parsing the body contents
        default_body_size = msg[0]['payload']['body']['size']
        contents['size'] = default_body_size
        body_data = []

        if default_body_size != 0:
            body_data.append(decode_base64(msg[0]['payload']['body']['data']))
        else:
            for parts in msg[0]['payload'].get('parts'):
                #log.info(parts)
                body_data.append(decode_base64(parts['body']['data']))

        
        contents['body'] = body_data

        mail_contents.append(contents)
        log.info(contents)
    #log.info(mail_contents)
        


if __name__ == "__main__":
    #account, account_pass = (sys.argv[1], sys.argv[2])
    config = read_config.read_config()
    log = get_logger.get_logger()

    folder = (sys.argv[1])

    read_gmail_contents(folder)