from dataclasses import dataclass
from datetime import datetime

from ticketstream.ticketing.domain.entities import event
from ticketstream.ticketing.domain.entities.event import Event


@dataclass(frozen=True)
class EventResponse:
    name: str
    description: str
    location: str
    start_at: datetime
    end_at: datetime
    reservable_quantity: int

    @classmethod
    def from_entity(cls, event_entity: Event) -> EventResponse:
        reservable_quantity = 0

        for category in event_entity.categories:
            reservable_quantity += category.reservable_quantity

        return cls(
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
