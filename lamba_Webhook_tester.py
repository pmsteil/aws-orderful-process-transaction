# File 7: Webhook_tester function

import boto3
import json
import os

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.environ['ConvertToEdiQueue'])

def lambda_handler(event, context):
    payload = {
        'isa': {
            'isa_id': '00',
            'isa_sender_id': 'sender',
            'isa_receiver_id': 'receiver',
            'isa_date': '210101',
            'isa_time': '0000',
            'isa_control_number': '000000000',
            'isa_use': 'U',
            'isa_test_indicator': 'T'
        },
        'gs': {
            'gs_id': 'sender',
            'gs_receiver_id': 'receiver',
            'gs_date': '210101',
            'gs_time': '0000',
            'gs_control_number': '000000000',
            'gs_responsible_agency_code': 'X',
            'gs_version': '004010'
        },
        'st': {
            'st_identifier_code': '204',
            'st_control_number': '0001'
        }
    }
    message = json.dumps(payload)
    queue.send_message(MessageBody=message)

    return {
        'statusCode': 200,
        'body': json.dumps('Webhook sent')
    }
