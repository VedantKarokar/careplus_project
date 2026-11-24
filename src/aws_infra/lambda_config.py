import boto3 as bt3
import os

class Lambda_func:
    def __init__(self, function_name: str, region: str):
        self.function = function_name
        self.region = region
        self.client = bt3.client('lambda', region_name=region)
        pass

    def create(self, code_file, **kwargs):
        try:
            return self.client.create_function(
                FunctionName=self.function,
                Runtime='python3.12',
                Role='...',
                Handler='...',
                Code={
                    'ZipFile': code_file
                },
                Timeout=30,
                PackageType='Zip',
                Layers=[
                    'string',
                ]
            )
        except:
            pass