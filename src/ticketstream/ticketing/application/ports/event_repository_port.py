from typing import Protocol

from ticketstream.ticketing.domain.entities.event import Event


class EventRepositoryPort(Protocol):
    def findById(self, event_id: str) -> Event: ...
    def findAll(self) -> list[Event]: ...
