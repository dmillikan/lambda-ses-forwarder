import json
import email

def process_event(event, context):
 
    for record in event['Records']:
        msgJson = json.loads(record['Sns']['Message'])
        msgSubject = msgJson['mail']['commonHeaders']['subject']

        msgContent = msgJson['content']

        msg = email.message_from_string(msgContent)

        st = ''
        if msg.get_content_type() == "text/plain":
                    st = str(msg.get_payload())
        else:    
            for payload in msg.get_payload():
                if payload.get_content_type() == "text/plain":
                    st = str(payload.get_payload())

        print(st)

    return
