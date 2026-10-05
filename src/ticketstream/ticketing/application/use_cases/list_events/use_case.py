from typing import Any

from ticketstream.ticketing.application.ports.event_repository_port import (
    EventRepositoryPort,
)
from ticketstream.ticketing.application.use_cases.list_events.response import (
    ListEventsResponse,
)


class ListEventsUseCase:
    def __init__(self, event_repository: EventRepositoryPort) -> None:
        self.event_repository = event_repository

    def execute(self, request: dict[str, Any]) -> ListEventsResponse:
        events = self.event_repository.findAll()
        return ListEventsResponse.from_entities(events)
