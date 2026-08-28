from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ticketstream.ticketing.domain.entities.ticket_category import TicketCategory


@dataclass(frozen=True, slots=True)
class Event:
    event_id: UUID
    name: str
    description: str
    location: str
    max_tickets_per_users: int
    categories: tuple[TicketCategory, ...]
    start_at: datetime
    end_at: datetime
