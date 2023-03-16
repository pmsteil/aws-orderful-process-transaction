# AWS EDI Project
## Status: Work in progress - pre-alpha

This project will create all resources and code for processing EDI files with Orderful and AWS.


These are the files we will use in this project:
- File 1: CloudFormation Stack
- File 2: Swagger File for API Gateway
- File 3: Lambda Function ProcessPayloadFunction
- File 4: Convert to EDI function
- File 5: EdiUpload function
- File 6: OrderConfirmTransaction function
- File 7: Webhook_tester function
- File 8: Unit Tests for each lambda function


# High level workflow

1. Orderful API Gateway: Create an API Gateway to receive the webhook payload from Orderful. Configure the API Gateway to trigger the "process-payload" Lambda function.

2. "process-payload" Lambda Function : This will
receive the webhook payload from the API Gateway
put a message on an SQS queue called "convert-to-edi-queue" with the json to convert

3. "convert-to-edi" Lambda Function: This Lambda function will be triggered by the messages in the "convert-to-edi-queue". This function will
use the Stedi API to convert the payload to EDI format
store the converted file in an S3 bucket named in the ENV variable: EDI_BUCKET_NAME
send a message to another SQS queue "edi-upload-queue".

4. "edi-upload" Lambda Function: This Lambda function will be triggered by messages in the "edi-process-queue". It will
upload the EDI file to the client's SFTP server using Python.
move the processed file to an "processed" folder in the S3 bucket
put a message on an SQS queue called "orderful-confirm-transaction-queue".

5. "orderful-confirm-transaction" Lambda Function: Triggered by messages in the "orderful-confirm-transaction-queue". It will then:
send a POST to the Orderful "confirm_transaction" REST API to send a confirmation message to Orderful.

6. Create a webhook_tester function to simulate the sending of a webhook to the "process_payload" api.  The payload should be a JSON object representing a "204 Purchase Order" X12 EDI file, but in JSON format.

7. Testing: Implement a testing framework to unit test each Lambda function in isolation and the entire system as a whole.

8. Use AWS Secret Manager and Environment manager to store:
ORDERFUL_API_KEY
EDI_BUCKET_NAME
EDI_BUCKET_FOLDER_PROCESSING
EDI_BUCKET_FOLDER_PROCESSED
EDI_BUCKET_FOLDER_ERRORS
SFTP_HOST
SFTP_USER
SFTP_PASS
SFTP_FOLDER_DESTINATION

9. All code will be fully documented.

10. Security: Ensure that all AWS resources are secured using the appropriate security mechanisms, such as IAM roles.  If necessary, create all the IAM roles, policies, etc needed.

11. Error handling: Implement appropriate error handling mechanisms in each Lambda function and use an "error-queue" to send error messages for further investigation.

12. Monitoring: Use CloudWatch Logging to log all significant events in the system.

13. Use AWS Metrics appropriately to instrument monitoring of the system.
