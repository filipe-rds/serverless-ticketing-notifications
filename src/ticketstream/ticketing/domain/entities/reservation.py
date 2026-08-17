from ticketstream.shared.domain.value_objects.non_empty_string import NonEmptyString
from ticketstream.shared.domain.value_objects.non_negative_integer import (
    NonNegativeInteger,
)
from ticketstream.ticketing.domain.value_objects.reservation_status import (
    ReservationStatus,
)


class Reservation:
    def __init__(
        self,
        id: NonEmptyString,
        user_id: NonEmptyString,
        ticket_category_id: NonEmptyString,
        quantity: NonNegativeInteger,
        status: ReservationStatus = ReservationStatus.PENDING,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._ticket_category_id = ticket_category_id
        self._quantity = quantity
        self._status = status

    @property
    def id(self) -> NonEmptyString:
        return self._id

    @property
    def user_id(self) -> NonEmptyString:
        return self._user_id

    @property
    def ticket_category_id(self) -> NonEmptyString:
        return self._ticket_category_id

    @property
    def quantity(self) -> NonNegativeInteger:
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
