from ticketstream.ticketing.domain.enumerators.reservation_status import (
    ReservationStatus,
)


class Reservation:
    def __init__(
        self,
        reservation_id: str,
        user_id: str,
        ticket_category_id: str,
        quantity: int,
        status: ReservationStatus = ReservationStatus.PENDING,
    ) -> None:
        self._reservation_id = reservation_id
        self._user_id = user_id
        self._ticket_category_id = ticket_category_id
        self._quantity = quantity
        self._status = status

    @property
    def reservation_id(self) -> str:
        return self.reservation_id

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def ticket_category_id(self) -> str:
        return self._ticket_category_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def status(self) -> ReservationStatus:
        return self._status

    def transition_to(self, next_status: ReservationStatus) -> None:
        if not self._status.can_trasition_to(next_status):
            raise ValueError(
                f"Invalid transition status: {self._status.value} -> {next_status.value}"
            )
        self._status = next_status
