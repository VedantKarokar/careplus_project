import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from logging_config.log_config import setup_logging

logger = setup_logging(name = "tickets")

load_dotenv()

lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
function_name = 'tickets_transformation'
bucket_name = os.getenv("AWS_BUCKET")
s3_key = 'support_tickets/raw/tickets.csv'

def create_trigger(lambda_func_name , s3_bucket_name):
    # Grant S3 permission to invoke the Lambda function
    lambda_client.add_permission(
        FunctionName = lambda_func_name,
        StatementId = 's3-ingestion-trigger-permission',
        Action = 'lambda:InvokeFunction',
        Principal = 's3.amazonaws.com',
        SourceArn = f'{os.getenv("S3_ARN")}',
        SourceAccount = f'{os.getenv("AWS_ACCOUNT_ID")}'
    )
    # Configure the S3 bucket notification trigger
    s3_client.put_bucket_notification_configuration( # This method will overwrite the notification rule for the bucket
        Bucket = s3_bucket_name,
        NotificationConfiguration={
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': os.getenv("LAMBDA_ARN"),
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'prefix', 'Value': 'support_tickets/raw/' 
                                    }
                            ]
                        }
                    }
                }
            ]
        }
    )

try:
    create_trigger(lambda_func_name = function_name, s3_bucket_name = bucket_name)
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'ResourceConflictException':
        logger.debug("Trigger created already.")
        pass
