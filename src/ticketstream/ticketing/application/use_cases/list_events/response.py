from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ticketstream.ticketing.domain.entities.event import Event


@dataclass(frozen=True)
class EventResponse:
    event_id: UUID
    name: str
    description: str
    location: str
    start_at: datetime
    end_at: datetime
    reservable_quantity: int

    @classmethod
    def from_entity(cls, event_entity: Event) -> EventResponse:
        reservable_quantity = sum(
            category.reservable for category in event_entity.categories
        )

        return cls(
            event_entity.event_id,
            event_entity.name,
            event_entity.description,
            event_entity.location,
            event_entity.start_at,
            event_entity.end_at,
            reservable_quantity,
        )


@dataclass(frozen=True)
class ListEventsResponse:
    events: tuple[EventResponse, ...]
    total: int

    @classmethod
    def from_entities(cls, event_entity_list: list[Event]) -> ListEventsResponse:
        events = tuple(EventResponse.from_entity(event) for event in event_entity_list)
        total = len(events)

        return cls(events, total)
