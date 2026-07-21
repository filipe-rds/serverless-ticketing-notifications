from typing import Annotated
from serverless_ticketing_notifications.ticketing.domain.type.non_empty_string import (
    NonEmptyString,
)
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"


class Reservation(BaseModel):
    model_config = ConfigDict(strict=True)

    id: NonEmptyString
    user_id: NonEmptyString
    ticket_tier_id: NonEmptyString
    quantity: Annotated[int, Field(ge=1)]
    status: ReservationStatus
