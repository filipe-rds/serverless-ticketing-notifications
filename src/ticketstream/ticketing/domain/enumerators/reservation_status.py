from enum import Enum


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

    def can_transition_to(self, next_status: ReservationStatus) -> bool:
        allowed: dict[ReservationStatus, set[ReservationStatus]] = {
            ReservationStatus.PENDING: {
                ReservationStatus.CONFIRMED,
                ReservationStatus.CANCELLED,
                ReservationStatus.EXPIRED,
            },
            ReservationStatus.CONFIRMED: set(),
            ReservationStatus.CANCELLED: set(),
            ReservationStatus.EXPIRED: set(),
        }

        return next_status in allowed[self]
