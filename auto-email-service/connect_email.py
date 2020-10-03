import read_config
import smtplib
import time
import imaplib
import email
import sys

def connect_to_gmail_server_unsecured(): 
    '''
        Try connecting to the email server
    '''
    mail = imaplib.IMAP4_SSL(config['EMAIL']['GMAIL']['SMTP_SERVER'])
    mail.login(account,account_pass)
    mail.select(config['EMAIL']['GMAIL']['DEFAULT_FOLDER'])

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


if __name__ == "__main__":
    account, account_pass = (sys.argv[1], sys.argv[2])
    config = read_config.read_config()
    connect_to_gmail_server_unsecured()
    
    