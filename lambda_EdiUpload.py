# File 5: EdiUpload function

import boto3
import os
import json
import pysftp

s3 = boto3.client('s3')
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.environ['OrderfulConfirmTransactionQueue'])

def lambda_handler(event, context):
    sftp = pysftp.Connection(os.environ['SftpHost'], username=os.environ['SftpUser'], password=os.environ['SftpPass'])
    for message in event['Records']:
        key = message['body']
        s3.download_file(os.environ['EDIBucketName'], key, '/tmp/' + key)
        try:
            sftp.put('/tmp/' + key, os.environ['SftpFolderDestination'] + '/' + key)
            s3.copy_object(Bucket=os.environ['EDIBucketName'], CopySource=os.environ['EDIBucketName'] + '/' + key, Key=os.environ['EdiBucketFolderProcessed'] + '/' + key)
            s3.delete_object(Bucket=os.environ['EDIBucketName'], Key=key)
            queue.send_message(MessageBody=key)
        except:
            s3.copy_object(Bucket=os.environ['EDIBucketName'], CopySource=os.environ['EDIBucketName'] + '/' + key, Key=os.environ['EdiBucketFolderErrors'] + '/' + key)
            s3.delete_object(Bucket=os.environ['EDIBucketName'], Key=key)
            queue.send_message(MessageBody=key)

    sftp.close()

    return {
        'statusCode': 200,
        'body': json.dumps('EDIs Uploaded')
    }
