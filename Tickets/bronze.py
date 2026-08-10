import os
import pandas as pd
import boto3
import logging
from db import db_config
from dotenv import load_dotenv
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import exc
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="Tickets/logs/bronze.log"
)

logger = logging.getLogger(__name__)

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

try:
    def began_ingestion():
        # Query data
        query = select(db_config.Tickets)
        df = pd.read_sql(sql=query, con=engine)
        if df.empty:
            print("No data found, skipping upload.")
        # upload to s3
        timestamp = datetime.now(datetime.astimezone.utc).strftime("%d%m%Y%H%M%S")
        s3_key = f"{aws_prefix}{timestamp}.csv"
        logger.info("Ingestion complete")
        return s3_upload(df, aws_bucket, s3_key)
    
except exc.SQLAlchemyError:
    logger.exception("Failed to read from database")
    raise

except exc.ClientError:
    logger.exception("Failed to upload to S3")
    raise
