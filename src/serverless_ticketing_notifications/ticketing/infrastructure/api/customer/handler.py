from serverless_ticketing_notifications.ticketing.infrastructure.api.customer.controller import (
    router,
)

from serverless_ticketing_notifications.ticketing.infrastructure.gateway.api_gateway_rest_resolver import (
    restApiResolver,
)

restApiResolver.include_router(router)


def lambda_handler(event, context):
    return restApiResolver.resolve(event, context)
