from typing import Protocol
from uuid import UUID

from ticketstream.ticketing.domain.entities.event import Event


class EventRepositoryPort(Protocol):
    def find_by_id(self, event_id: UUID) -> Event | None: ...
    def find_all(self) -> list[Event]: ...
