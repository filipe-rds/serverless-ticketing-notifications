from ticketstream.shared.exceptions.app_exception import AppException


class ApplicationException(AppException):
    """Flow and orchestration errors—no business rule."""

    pass
