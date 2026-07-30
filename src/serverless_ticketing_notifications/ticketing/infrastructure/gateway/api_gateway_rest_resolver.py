from aws_lambda_powertools.event_handler import APIGatewayRestResolver

restApiResolver = APIGatewayRestResolver()

# restApiResolver = APIGatewayRestResolver(
#     enable_validation=True,
#     response_validation_error_http_code=HTTPStatus.INTERNAL_SERVER_ERROR,
# )
