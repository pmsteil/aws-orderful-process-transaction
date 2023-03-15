# File 4: Convert to EDI function

import boto3
import os
import json
import stedi_sdk as stedi

s3 = boto3.client('s3')
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.environ['EdiUploadQueue'])

def lambda_handler(event, context):
    for message in event['Records']:
        payload = json.loads(message['body'])
        converted = stedi.convert_to_edi(payload)
        s3.put_object(Bucket=os.environ['EDIBucketName'], Key='filename.edi', Body=converted)
        queue.send_message(MessageBody='filename.edi')

    return {
        'statusCode': 200,
        'body': json.dumps('EDIs Converted')
    }

