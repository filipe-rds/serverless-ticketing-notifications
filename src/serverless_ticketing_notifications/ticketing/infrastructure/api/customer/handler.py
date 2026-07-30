import json


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {"controller": "Customer", "message": "Customer controller is running!"}
        ),
    }
