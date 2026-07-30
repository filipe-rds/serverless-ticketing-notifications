import json
from serverless_ticketing_notifications.ticketing.infrastructure.api.customer.controller import (
    router,
)

from serverless_ticketing_notifications.ticketing.infrastructure.gateway.api_gateway_rest_resolver import (
    restApiResolver,
)

restApiResolver.include_router(router, prefix="/")


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {"controller": "Customer", "message": "Customer controller is running!"}
        ),
    }
