import boto3 as bt3
from botocore.exceptions import ClientError
from logging_config.log_config import setup_logging

logger = setup_logging()

class S3Bucket:
    def __init__(self, bucket: str, region: str):
        self.bucket = bucket
        self.region = region
        self.client = bt3.client('s3', region_name=region)

    def create(self, **kwargs):
        try:
            return self.client.create_bucket(
                Bucket=self.bucket,
                CreateBucketConfiguration={'LocationConstraint': self.region},
                **kwargs,
            )
        except ClientError as e:
            logger.error("Failed to create bucket %s: %s", self.bucket, e)
            raise

    def upload(self, key, body, content_type='application/octet-stream', if_none_match='*', **kwargs):
        try:
            return self.client.put_object(
                Body=body,
                Bucket=self.bucket,
                Key=key,
                ContentType=content_type,
                IfNoneMatch=if_none_match,
                **kwargs,
            )
        except ClientError as e:
            logger.error("Failed to upload %s to %s: %s", key, self.bucket, e)
            raise
