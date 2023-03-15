# Yes, I can definitely help you with that. Here's a Pulumi Python script that creates the architecture described in your requirements:

# Note that the above script assumes that you have written the Lambda function code and stored it in separate directories named `process_payload_function`, `convert_to_edi_function`, `edi_upload_function`, `orderful_confirm_transaction_function`, and `webhook_tester_function`. You will need to create these directories and write the Lambda function code yourself.

# Also, this script assumes that you have already created an AWS Secrets Manager secret named `orderful-api-key` that contains the Orderful API key. You will need to create this secret yourself and configure its value accordingly.


import pulumi
import pulumi_aws as aws
import pulumi_random as random

# Create an S3 bucket to store EDI files
edi_bucket = aws.s3.Bucket('edi-bucket')

# Create an SQS queue for the "convert-to-edi" Lambda function
convert_to_edi_queue = aws.sqs.Queue('convert-to-edi-queue')

# Create an SQS queue for the "edi-upload" Lambda function
edi_upload_queue = aws.sqs.Queue('edi-upload-queue')

# Create an SQS queue for the "orderful-confirm-transaction" Lambda function
orderful_confirm_transaction_queue = aws.sqs.Queue('orderful-confirm-transaction-queue')

# Create an IAM role for the "process-payload" Lambda function
process_payload_role = aws.iam.Role('process-payload-role',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }"""
)

# Attach the AWSLambdaBasicExecutionRole policy to the process_payload_role
aws.iam.RolePolicyAttachment('process-payload-policy-attachment',
    policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
    role=process_payload_role.name
)

# Create an IAM role for the "convert-to-edi" Lambda function
convert_to_edi_role = aws.iam.Role('convert-to-edi-role',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }"""
)

# Attach the AWSLambdaBasicExecutionRole policy to the convert_to_edi_role
aws.iam.RolePolicyAttachment('convert-to-edi-policy-attachment',
    policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
    role=convert_to_edi_role.name
)

# Create an IAM role for the "edi-upload" Lambda function
edi_upload_role = aws.iam.Role('edi-upload-role',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }"""
)

# Attach the AWSLambdaBasicExecutionRole policy to the edi_upload_role
aws.iam.RolePolicyAttachment('edi-upload-policy-attachment',
    policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
    role=edi_upload_role.name
)

# Create an IAM role for the "orderful-confirm-transaction" Lambda function
orderful_confirm_transaction_role = aws.iam.Role('orderful-confirm-transaction-role',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }"""
)

# Attach the AWSLambdaBasicExecutionRole policy to the orderful_confirm_transaction_role
aws.iam.RolePolicyAttachment('orderful-confirm-transaction-policy-attachment',
    policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
    role=orderful_confirm_transaction_role.name
)

# Define the "process-payload" Lambda function
process_payload_function = aws.lambda_.Function('process-payload-function',
    runtime=aws.lambda_.Runtime.PYTHON_3_8,
    handler='handler.process_payload',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./process_payload_function')
    }),
    role=process_payload_role.arn,
    environment={
        'QUEUE_URL': convert_to_edi_queue.url
    }
)

# Define the "convert-to-edi" Lambda function
convert_to_edi_function = aws.lambda_.Function('convert-to-edi-function',
    runtime=aws.lambda_.Runtime.PYTHON_3_8,
    handler='handler.convert_to_edi',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./convert_to_edi_function')
    }),
    role=convert_to_edi_role.arn,
    environment={
        'QUEUE_URL': edi_upload_queue.url,
        'EDI_BUCKET_NAME': edi_bucket.id
    }
)

# Define the "edi-upload" Lambda function
edi_upload_function = aws.lambda_.Function('edi-upload-function',
    runtime=aws.lambda_.Runtime.PYTHON_3_8,
    handler='handler.edi_upload',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./edi_upload_function')
    }),
    role=edi_upload_role.arn,
    environment={
        'QUEUE_URL': orderful_confirm_transaction_queue.url,
        'EDI_BUCKET_NAME': edi_bucket.id
    }
)

# Define the "orderful-confirm-transaction" Lambda function
orderful_confirm_transaction_function = aws.lambda_.Function('orderful-confirm-transaction-function',
    runtime=aws.lambda_.Runtime.PYTHON_3_8,
    handler='handler.orderful_confirm_transaction',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./orderful_confirm_transaction_function')
    }),
    role=orderful_confirm_transaction_role.arn,
    environment={
        'ORDERFUL_API_KEY': aws.secretsmanager.SecretVersion.get_by_secret_name('orderful-api-key').secret_string,
    }
)

# Create an API Gateway to receive the webhook payload from Orderful
api_gateway = aws.apigatewayv2.Api('orderful-api-gateway',
    protocol_type='HTTP',
    route_key='POST /process-payload',
    target=process_payload_function.arn,
)

# Add permission for the API Gateway to invoke the "process-payload" Lambda function
api_gateway_permission = aws.lambda_.Permission('orderful-api-gateway-permission',
    action='lambda:InvokeFunction',
    function=process_payload_function.name,
    principal='apigateway.amazonaws.com',
    source_arn=api_gateway.execution_arn,
)

# Define the webhook_tester function
webhook_tester_function = aws.lambda_.Function('webhook-tester-function',
    runtime=aws.lambda_.Runtime.PYTHON_3_8,
    handler='handler.webhook_tester',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./webhook_tester_function')
    }),
    environment={
        'API_ENDPOINT': api_gateway.api_endpoint,
    }
)

# Create a CloudWatch log group for each Lambda function
process_payload_log_group = aws.cloudwatch.LogGroup('process-payload-log-group',
    name=f'/aws/lambda/{process_payload_function.name}'
)

convert_to_edi_log_group = aws.cloudwatch.LogGroup('convert-to-edi-log-group',
    name=f'/aws/lambda/{convert_to_edi_function.name}'
)

edi_upload_log_group = aws.cloudwatch.LogGroup('edi-upload-log-group',
    name=f'/aws/lambda/{edi_upload_function.name}'
)

orderful_confirm_transaction_log_group = aws.cloudwatch.LogGroup('orderful-confirm-transaction-log-group',
    name=f'/aws/lambda/{orderful_confirm_transaction_function.name}'
)

webhook_tester_log_group = aws.cloudwatch.LogGroup('webhook-tester-log-group',
    name=f'/aws/lambda/{webhook_tester_function.name}'
)

# Create an SQS queue for error messages
error_queue = aws.sqs.Queue('error-queue')

# Add permission for each Lambda function to send messages to the error queue
process_payload_error_permission = aws.sqs.QueuePolicy('process-payload-error-permission',
    policy=pulumi.Output.all(error_queue.arn, process_payload_function.arn).apply(lambda args: f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "process-payload-error-statement",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "sqs:SendMessage",
                "Resource": "{args[0]}",
                "Condition": {{
                    "ArnEquals": {{
                        "aws:SourceArn": "{args[1]}"
                    }}
                }}
            }}
        ]
    }}"""),
    queues=[error_queue.id]
)

convert_to_edi_error_permission = aws.sqs.QueuePolicy('convert-to-edi-error-permission',
    policy=pulumi.Output.all(error_queue.arn, convert_to_edi_function.arn).apply(lambda args: f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "convert-to-edi-error-statement",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "sqs:SendMessage",
                "Resource": "{args[0]}",
                "Condition": {{
                    "ArnEquals": {{
                        "aws:SourceArn": "{args[1]}"
                    }}
                }}
            }}
        ]
    }}"""),
    queues=[error_queue.id]
)

edi_upload_error_permission = aws.sqs.QueuePolicy('edi-upload-error-permission',
    policy=pulumi.Output.all(error_queue.arn, edi_upload_function.arn).apply(lambda args: f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "edi-upload-error-statement",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "sqs:SendMessage",
                "Resource": "{args[0]}",
                "Condition": {{
                    "ArnEquals": {{
                        "aws:SourceArn": "{args[1]}"
                    }}
                }}
            }}
        ]
    }}"""),
    queues=[error_queue.id]
)

orderful_confirm_transaction_error_permission = aws.sqs.QueuePolicy('orderful-confirm-transaction-error-permission',
    policy=pulumi.Output.all(error_queue.arn, orderful_confirm_transaction_function.arn).apply(lambda args: f"""{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "orderful-confirm-transaction-error-statement",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "sqs:SendMessage",
                "Resource": "{args[0]}",
                "Condition": {{
                    "ArnEquals": {{
                        "aws:SourceArn": "{args[1]}"
                    }}
                }}
            }}
        ]
    }}"""),
    queues=[error_queue.id]
)

# Export the API Gateway URL
pulumi.export('api_gateway_url', api_gateway.api_endpoint)

# Export the webhook_tester function name
pulumi.export('webhook_tester_function_name', webhook_tester_function.name)

# Export the error queue URL
pulumi.export('error_queue_url', error_queue.url)

# Export the S3 bucket name
pulumi.export('edi_bucket_name', edi_bucket.id)

# Export the IAM role ARNs
pulumi.export('process_payload_role_arn', process_payload_role.arn)
pulumi.export('convert_to_edi_role_arn', convert_to_edi_role.arn)
pulumi.export('edi_upload_role_arn', edi_upload_role.arn)
pulumi.export('orderful_confirm_transaction_role_arn', orderful_confirm_transaction_role.arn)


