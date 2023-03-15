# File 3: Lambda Function ProcessPayloadFunction

import boto3
import json
import os

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.environ['ConvertToEdiQueue'])

def lambda_handler(event, context):
    body = json.loads(event['body'])
    message = json.dumps(body)
    queue.send_message(MessageBody=message)

    return {
        'statusCode': 200,
        'body': json.dumps('Payload processed')
    }

