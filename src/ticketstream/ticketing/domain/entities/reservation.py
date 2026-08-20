from dataclasses import dataclass, replace

from ticketstream.ticketing.domain.enumerators.reservation_status import (
    ReservationStatus,
)


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    ticket_category_id: str
    user_id: str
    quantity: int
    status: ReservationStatus

    def __post_init__(self) -> None:
        if not self.reservation_id.strip():
            raise ValueError("Reservation id cannot be empty")

        if not self.ticket_category_id.strip():
            raise ValueError("Reservation ticket category id cannot be empty")

        if not self.user_id.strip():
            raise ValueError("Reservation user id cannot be empty")

        if self.quantity <= 0:
            raise ValueError("Reservation quantity must be greater than zero")

        if self.status is None:
            raise ValueError("Reservation status cannot be empty")

    def confirm(self) -> Reservation:
        if not self.status.can_transition_to(ReservationStatus.CONFIRMED):
            raise ValueError("Reservation status cannot be confirmed")

        return replace(self, status=ReservationStatus.CONFIRMED)

    def cancel(self) -> Reservation:
        if not self.status.can_transition_to(ReservationStatus.CANCELLED):
            raise ValueError("Reservation status cannot be cancelled")

        return replace(self, status=ReservationStatus.CANCELLED)
