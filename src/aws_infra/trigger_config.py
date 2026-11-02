import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from logging_config.log_config import setup_logging

logger = setup_logging(name = "logs")

load_dotenv()

lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def create_trigger(lambda_func_name:str , s3_bucket_name:str, s3_object_key:str):
    # Grant S3 permission to invoke the Lambda function
    try:
        lambda_client.add_permission(
            FunctionName = lambda_func_name,
            StatementId = 's3-ingestion-trigger-permission',
            Action = 'lambda:InvokeFunction',
            Principal = 's3.amazonaws.com',
            SourceArn = f'arn:aws:s3:::{os.getenv("AWS_BUCKET")}',
            SourceAccount = f'{os.getenv("AWS_ACCOUNT_ID")}'
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceConflictExcecption':
            raise
    new_config = {
            'Id': f"{lambda_func_name}-trigger",
            'LambdaFunctionArn': f'arn:aws:s3:::{os.getenv("AWS_BUCKET")}',
            'Events': ['s3:ObjectCreated:*'],
            'Filter': {
                'Key': {
                    'FilterRules': [
                        {
                            'Name': 'prefix', 
                            'Value': s3_object_key
                        }
                    ]
                }
            }
        }
    # Fetch existing notification config so we don't clobber other triggers (e.g. tickets)
    try:
        existing = s3_client.get_bucket_notification_configuration(Bucket=s3_bucket_name)
    except ClientError:
        existing = {}

    configs = [conf for conf in existing.get('LambdaFunctionConfigurations', [])
                if conf.get('LambdaFunctionArn') != f'arn:aws:s3:::{os.getenv("AWS_BUCKET")}']
    configs.append(new_config)

    notification = {'LambdaFunctionConfigurations':configs}
    for key in ('TopicConfigurations', 'QueueConfigurations', 'EventBridgeConfiguration'):
        if key in existing:
            notification[key] = existing[key]

    s3_client.put_bucket_notification_configuration(
        Bucket=s3_bucket_name,
        NotificationConfiguration=notification
    )

try:
    create_trigger(lambda_func_name='logs_transformation', s3_bucket_name=os.getenv("AWS_BUCKET"), s3_object_key='support_logs/raw/')
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'ResourceConflictException':
        logger.debug("Trigger created already.")
    else:
        raise
