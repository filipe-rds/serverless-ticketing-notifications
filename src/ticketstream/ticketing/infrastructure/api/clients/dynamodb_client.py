import os

from pydynox import DynamoDBClient, set_default_client

dynamodb_client = DynamoDBClient(region=os.getenv("AWS_REGION"))
set_default_client(dynamodb_client)
