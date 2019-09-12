import json
import email
import boto3
import os

def process_event(event, context):
    """Forward the mail"""
    ses_client = boto3.client('ses')
    emailAddress = os.environ['RECEPIENT_EMAIL']
    for record in event['Records']:
        # print(record['Sns']['Message'])
        msgJson = json.loads(record['Sns']['Message'])
        subject = 'FW:' + msgJson['mail']['commonHeaders']['subject']
        # print(msgJson)

        # print("Mail Subject IS : {0}".format(subject))
        
        msgContent = msgJson['content']

        for msg in email.message_from_string(msgContent).get_payload():
            if msg.get_content_type() == "text/plain":
                st = str(msg.get_payload())
            elif msg.get_content_type() == "text/html":
                html = str(msg.get_payload())
        

        response = ses_client.send_email(
            Source=emailAddress,
            Destination={'ToAddresses': [emailAddress]},
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': html
                    },
                    'Text': {
                        'Data': st,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print(response)
    return
