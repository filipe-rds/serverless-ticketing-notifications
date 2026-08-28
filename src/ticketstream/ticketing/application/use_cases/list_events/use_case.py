from typing import Any

from ticketstream.ticketing.application.use_cases.list_events.response import (
    ListEventsResponse,
)
from ticketstream.ticketing.domain.repositories.event_repository_interface import (
    EventRepositoryInterface,
)


class ListEventsUseCase:
    def __init__(self, event_repository: EventRepositoryInterface) -> None:
        self.event_repository = event_repository

    def execute(self, command: dict[str, Any]) -> ListEventsResponse:
        events = self.event_repository.findAll()
        return ListEventsResponse.from_entities(events)
