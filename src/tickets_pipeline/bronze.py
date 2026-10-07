import os
import pandas as pd
import boto3
from dotenv import load_dotenv
from io import StringIO
from sqlalchemy import select
from sqlalchemy import exc
from logging_config.log_config import setup_logging
from tickets_pipeline.db.db_config import Tickets, engine
from botocore.exceptions import ClientError

logger = setup_logging(name = "tickets")

load_dotenv()

def s3_upload(df, bucket, key):
    # Buffer(file like object on memory) for AWS
    csv_buffer = StringIO()
    df.to_csv(
        csv_buffer,
        index = False
        )  # We write to the file like object created on memory
    s3=boto3.client(
        service_name = 's3'
        )
    s3.put_object(
        Bucket = bucket,
        Key = key,
        Body = csv_buffer.getvalue(), # Retrieve contents as a string
        IfNoneMatch = '*'  # Fails if key already exists
        )

def began_ingestion():
        logger.info("Bronze layer ingestion started for tickets_pipeline")
        # Query data
        query = select(Tickets)
        df = pd.read_sql(sql=query, con=engine)
        if df.empty:
            logger.debug("Data was not found, upload was skipped.")
        else:
            # upload to s3
            s3_key = f"support_tickets/raw/tickets.csv"
            return s3_upload(df = df, bucket = os.getenv("AWS_BUCKET"), key = s3_key)

try:
    began_ingestion()
    logger.info("Files Successfully Ingested.")

except exc.SQLAlchemyError:
    logger.error("Failed to read from database")
    raise

except ClientError as e:
    if e.response['Error']['Code'] in ('412', 'PreconditionFailed'):
        print("Duplicate object detected! Ingestion stopped.")
        logger.debug("Data already exists, ingestion stopped.")
    else:
        logger.exception("Failed to upload to S3")
        raise
