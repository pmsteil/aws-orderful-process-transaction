# File 6: OrderConfirmTransaction function

import boto3
import os
import json
import requests

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.environ['OrderfulConfirmTransactionQueue'])

def lambda_handler(event, context):
    for message in event['Records']:
        payload = {
            'transaction_id': message['body']
        }
        headers = {
            'Authorization': os.environ['ORDERFUL_API_KEY']
        }
        response = requests.post('https://api.orderful.com/confirm_transaction', headers=headers, data=payload)
        if response.status_code == 200:
            queue.delete_messages(Entries=[{'Id': message['messageId'], 'ReceiptHandle': message['receiptHandle']}])

    return {
        'statusCode': 200,
        'body': json.dumps('Transactions Confirmed')
    }

