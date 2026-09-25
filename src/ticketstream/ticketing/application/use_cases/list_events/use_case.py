from typing import Any

from ticketstream.ticketing.application.ports import EventRepositoryPort
from ticketstream.ticketing.application.use_cases.list_events.response import (
    ListEventsResponse,
)


class ListEventsUseCase:
    def __init__(self, event_repository: EventRepositoryPort) -> None:
        self._event_repository = event_repository

    def execute(self, request: dict[str, Any]) -> ListEventsResponse:
        events = self._event_repository.find_all()
        return ListEventsResponse.from_entities(events)
