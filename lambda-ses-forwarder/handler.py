import json
import boto3
from botocore.exceptions import ClientError
import os
import urllib
import sys
import uuid
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def process_event(event, context):
    """Forward the mail"""
    client = boto3.client('ses')
    emailAddress = os.environ['RECEPIENT_EMAIL']
    s3_client = boto3.client('s3')
    
    for record in event['Records']:
        # print(record['Sns']['Message'])
        msgJson = json.loads(record['Sns']['Message'])
        bucket_name = msgJson['receipt']['action']['bucketName']
        object_key = msgJson['receipt']['action']['objectKey']

        # print('File {0} is in bucket {1}'.format(object_key,bucket_name))
        
        ATTACHMENT = '/tmp/{0}{1}.eml'.format(uuid.uuid4(), object_key)
        s3_client.download_file(bucket_name, object_key, ATTACHMENT)

        msg = MIMEMultipart('mixed')
        # Add subject, from and to lines.
        msg['Subject'] = 'Forwarded Message from cf-training@dmillikan.com'
        msg['From'] = emailAddress
        msg['To'] = emailAddress
        BODY_TEXT = 'see attached file'
        BODY_HTML = '<html><head></head><body>{0}</body></html>'.format(BODY_TEXT)
        CHARSET = "utf-8"
        msg_body = MIMEMultipart('alternative')

        textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
        htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

        msg_body.attach(textpart)
        msg_body.attach(htmlpart)

        att = MIMEApplication(open(ATTACHMENT, 'rb').read())

        att.add_header('Content-Disposition', 'attachment',
                       filename=os.path.basename(ATTACHMENT))


        msg.attach(msg_body)

        # Add the attachment to the parent container.
        msg.attach(att)
        #print(msg)
        try:
            #Provide the contents of the email.
            response = client.send_raw_email(
                Source=emailAddress,
                Destinations=[emailAddress],
                RawMessage={
                    'Data': msg.as_string()
                }
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            s3_object = s3_client.Object(bucket_name,object_key)
            s3_object.delete()

    return
