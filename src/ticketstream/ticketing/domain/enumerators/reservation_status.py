from enum import Enum


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

    def can_trasition_to(self, next_status: ReservationStatus) -> bool:
        allowed = {
            ReservationStatus.PENDING: {
                ReservationStatus.CONFIRMED,
                ReservationStatus.CANCELLED,
            },
            ReservationStatus.CONFIRMED: {ReservationStatus.CANCELLED},
            ReservationStatus.CANCELLED: set(),
        }

        return next_status in allowed[next_status]
