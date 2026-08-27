from ticketstream.shared.exceptions.app_exception import AppException


class InfrastructureException(AppException):
    """Technical errors — bank, network, external services."""

    pass
