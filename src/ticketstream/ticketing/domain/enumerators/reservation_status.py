from enum import Enum


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

    @staticmethod
    def can_transition_to(next_status: ReservationStatus) -> bool:
        allowed = {
            ReservationStatus.PENDING: {
                ReservationStatus.CONFIRMED,
                ReservationStatus.CANCELLED,
            },
            ReservationStatus.CONFIRMED: {ReservationStatus.CANCELLED},
            ReservationStatus.CANCELLED: set(),
        }

        return next_status in allowed[next_status]
