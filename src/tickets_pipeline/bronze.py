import os
import pandas as pd
import boto3
from dotenv import load_dotenv
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import exc
from datetime import datetime, timezone
from logging_config.log_config import setup_logging
from tickets_pipeline.db import Tickets

logger = setup_logging(name = "tickets")

load_dotenv()

aws_bucket="careplusstorage"
aws_prefix="support_tickets/raw/"

engine = create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}",pool_pre_ping=False)

def s3_upload(df, bucket, key):
    # Buffer for AWS
    csv_buffer=StringIO()
    df.to_csv(
        csv_buffer,
        index=False
        )
    s3=boto3.client(
        service_name='s3'
        )
    boto3.s3.transfer.TransferConfig(
        multipart_chunksize=2
        )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=csv_buffer.getvalue()
        )

def began_ingestion():
        # Query data
        query = select(Tickets)
        df = pd.read_sql(sql=query, con=engine)
        if df.empty:
            logger.debug("Data was not found, upload was skipped.")
            print("No data found, skipping upload.")
        # upload to s3
        timestamp = datetime.now(timezone.utc).strftime("%d%m%Y%H%M%S")
        s3_key = f"{aws_prefix}{timestamp}.csv"
        return s3_upload(df, aws_bucket, s3_key)

try:
    began_ingestion()
    logger.debug("Ingestion complete")

except exc.SQLAlchemyError:
    logger.exception("Failed to read from database")

except boto3.exceptions.ClientError:
    logger.exception("Failed to upload to S3")
