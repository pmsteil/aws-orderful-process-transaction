
# File 8: Unit Tests for each lambda function


import json
import unittest
from unittest.mock import patch, MagicMock
import boto3
from moto import mock_s3, mock_sqs
from botocore.exceptions import ClientError
import requests
from requests.models import PreparedRequest

class TestProcessPayloadFunction(unittest.TestCase):
    @mock_sqs
    def test_process_payload_function(self):
        sqs = boto3.client('sqs', region_name='us-east-1')
        queue_url = sqs.create_queue(QueueName='convert-to-edi-queue')['QueueUrl']
        event = {
            'body': json.dumps({
                'key1': 'value1',
                'key2': 'value2'
            })
        }

        with patch('boto3.resource') as mock_resource:
            mock_queue = MagicMock()
            mock_resource.return_value = mock_queue
            mock_queue.get_queue_by_name.return_value = MagicMock()
            response = lambda_function.lambda_handler(event, None)
            messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
            self.assertEqual(len(messages['Messages']), 1)
            self.assertEqual(response['statusCode'], 200)

class TestConvertToEdiFunction(unittest.TestCase):
    @mock_sqs
    def test_convert_to_edi_function(self):
        sqs = boto3.client('sqs', region_name='us-east-1')
        queue_url = sqs.create_queue(QueueName='edi-upload-queue')['QueueUrl']
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        s3.put_object(Bucket='test-bucket', Key='test-key', Body=json.dumps({
            'key1': 'value1',
            'key2': 'value2'
        }))
        event = {
            'Records': [
                {
                    'body': json.dumps({
                        'key': 'test-key'
                    })
                }
            ]
        }

        with patch('stedi_sdk.Stedi.convert_to_edi') as mock_convert:
            mock_convert.return_value = 'EDI File'
            response = lambda_function.lambda_handler(event, None)
            messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
            self.assertEqual(len(messages['Messages']), 1)
            self.assertEqual(response['statusCode'], 200)

class TestEdiUploadFunction(unittest.TestCase):
    @mock_sqs
    @mock_s3
    @patch('pysftp.Connection')
    def test_edi_upload_function(self, mock_sftp):
        queue_url = boto3.client('sqs', region_name='us-east-1').create_queue(QueueName='orderful-confirm-transaction-queue')['QueueUrl']
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        s3.put_object(Bucket='test-bucket', Key='test-key', Body=json.dumps({
            'key1': 'value1',
            'key2': 'value2'
        }))
        event = {
            'Records': [
                {
                    'body': 'test-key'
                }
            ]
        }

        mock_sftp.return_value.__enter__.return_value = MagicMock()
        mock_sftp.return_value.__enter__.return_value.put.return_value = None

        with patch('boto3.client') as mock_client:
            mock_client.return_value.copy_object.return_value = None
            mock_client.return_value.delete_object.return_value = None
            response = lambda_function.lambda_handler(event, None)
            messages = boto3.resource('sqs',region_name='us-east-1').get_queue_by_name(QueueName='orderful-confirm-transaction-queue').receive_messages(MaxNumberOfMessages=10)
            self.assertEqual(len(messages), 1)
            self.assertEqual(response['statusCode'], 200)

    @mock_sqs
    @mock_s3
    @patch('pysftp.Connection')
    def test_edi_upload_function_error(self, mock_sftp):
        queue_url = boto3.client('sqs', region_name='us-east-1').create_queue(QueueName='orderful-confirm-transaction-queue')['QueueUrl']
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        s3.put_object(Bucket='test-bucket', Key='test-key', Body=json.dumps({
            'key1': 'value1',
            'key2': 'value2'
        }))
        event = {
            'Records': [
                {
                    'body': 'test-key'
                }
            ]
        }

        mock_sftp.return_value.__enter__.return_value = MagicMock()
        mock_sftp.return_value.__enter__.return_value.put.side_effect = Exception('Error')

        with patch('boto3.client') as mock_client:
            mock_client.return_value.copy_object.return_value = None
            mock_client.return_value.delete_object.return_value = None
            response = lambda_function.lambda_handler(event, None)
            messages = boto3.resource('sqs', region_name='us-east-1').get_queue_by_name(QueueName='orderful-confirm-transaction-queue').receive_messages(MaxNumberOfMessages=10)
            self.assertEqual(len(messages), 1)
            self.assertEqual(response['statusCode'], 200)

class TestOrderConfirmTransactionFunction(unittest.TestCase):
    @mock_sqs
    def test_order_confirm_transaction_function(self):
        sqs = boto3.client('sqs', region_name='us-east-1')
        queue_url = sqs.create_queue(QueueName='orderful-confirm-transaction-queue')['QueueUrl']
        event = {
            'Records': [
                {
                    'body': 'test-transaction-id'
                }
            ]
        }

        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.status_code = 200
            response = lambda_function.lambda_handler(event, None)
            messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
            self.assertEqual(len(messages['Messages']), 1)
            self.assertEqual(response['statusCode'], 200)

    @mock_sqs
    def test_order_confirm_transaction_function_error(self):
        sqs = boto3.client('sqs', region_name='us-east-1')
        queue_url = sqs.create_queue(QueueName='orderful-confirm-transaction-queue')['QueueUrl']
        event = {
            'Records': [
                {
                    'body': 'test-transaction-id'
                }
            ]
        }

        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.status_code = 500
            response = lambda_function.lambda_handler(event, None)
            messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
            self.assertEqual(len(messages['Messages']), 0)
            self.assertEqual(response['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()
