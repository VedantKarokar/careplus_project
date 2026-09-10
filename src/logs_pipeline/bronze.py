import boto3
from dotenv import load_dotenv
from io import BytesIO
from datetime import date, timedelta
from botocore.exceptions import ClientError
from logging_config.log_config import setup_logging

logger = setup_logging(name = "logs")

load_dotenv()

aws_bucket="careplusstorage"
aws_prefix="support_logs/raw/"

def s3_upload(bucket, key, body):
    s3 = boto3.client(
        service_name = 's3'
        )
    s3.put_object(
        Bucket = bucket,
        Key = key,
        Body = body,
        IfNoneMatch = '*'  # Fails if key already exists
        )

def began_ingestion():
    logger.info("Bronze layer ingestion started for logs_pipeline")
    start_date = date(2025, 6, 30)
    for i in range(1,32):
        # Buffer for AWS
        csv_buffer = BytesIO()

        new_date = start_date + timedelta(days = i)

        filepath = f"src/logs_pipeline/data/support_logs_{new_date}.log"

        with open(filepath, mode = 'r', encoding = 'utf-8') as f:
            content = f.read()
            csv_buffer.write(content.encode("utf-8")) 
            # log file's content is written to the buffer and converted from str to bytes

        s3_upload(
            bucket = aws_bucket,
            key = f"{aws_prefix}{new_date}",
            body = csv_buffer.getvalue()
            )
        print(f"File {new_date} ingested.")

try:
    began_ingestion()
    logger.info("Files Successfully Ingested.")

except ClientError as e:
    if e.response['Error']['Code'] in ('412', 'PreconditionFailed'):
        print("Duplicate object detected! Ingestion stopped.")
        logger.debug("Data already exists, ingestion stopped.")
    else:
        logger.exception("Failed to upload to S3")
        raise
