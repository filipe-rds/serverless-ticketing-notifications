from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ticketstream.ticketing.domain.enumerators.reservation_status import (
    ReservationStatus,
)


@dataclass(frozen=True, slots=True)
class Reservation:
    reservation_id: UUID
    ticket_category_id: UUID
    user_id: UUID
    quantity: int
    status: ReservationStatus
    created_at: datetime
    expires_at: datetime
    updated_at: datetime
