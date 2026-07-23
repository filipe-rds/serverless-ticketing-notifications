from typing import Annotated
from serverless_ticketing_notifications.ticketing.domain.type.non_empty_string import (
    NonEmptyString,
)
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Reservation(BaseModel):
    model_config = ConfigDict(strict=True)

    id: NonEmptyString
    user_id: NonEmptyString
    ticket_tier_id: NonEmptyString
    quantity: Annotated[int, Field(ge=1)]
    status: Annotated[ReservationStatus, Field(default=ReservationStatus.PENDING)]

    def confirm(self) -> None:
        if self.status != ReservationStatus.PENDING:
            raise ValueError("Only pending reservations can be confirmed.")
        self.status = ReservationStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status != ReservationStatus.PENDING:
            raise ValueError("Only pending reservations can be canceled.")
        self.status = ReservationStatus.CANCELLED

    def expire(self) -> None:
        if self.status != ReservationStatus.PENDING:
            raise ValueError("Only pending reservations can be expired.")
        self.status = ReservationStatus.EXPIRED
