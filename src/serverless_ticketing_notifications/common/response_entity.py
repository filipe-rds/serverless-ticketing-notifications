from http import HTTPStatus
from typing import Any

from aws_lambda_powertools.event_handler import Response

JSON_CONTENT_TYPE = "application/json"


class ResponseEntity:
    @staticmethod
    def ok(data: Any = None, message: str = "OK") -> Response:
        return ResponseEntity._json_response(
            status_code=HTTPStatus.OK,
            message=message,
            data=data,
        )

    @staticmethod
    def created(data: Any = None, message: str = "Created") -> Response:
        return ResponseEntity._json_response(
            status_code=HTTPStatus.CREATED,
            message=message,
            data=data,
        )

    @staticmethod
    def no_content() -> Response:
        return Response(
            status_code=HTTPStatus.NO_CONTENT,
            content_type=JSON_CONTENT_TYPE,
        )

    @staticmethod
    def _json_response(
        status_code: HTTPStatus,
        message: str,
        data: Any = None,
    ) -> Response:
        body: dict[str, Any] = {"message": message}

        if data is not None:
            body["data"] = data

        return Response(
            status_code=status_code.value,
            content_type=JSON_CONTENT_TYPE,
            body=body,
        )
