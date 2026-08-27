from ticketstream.shared.exceptions.app_exception import AppException


class DomainException(AppException):
    """Violations of business rules."""

    pass
