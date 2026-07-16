from serverless_ticketing_notifications.ticketing.domain.enums import ReservationStatus
from typing import Annotated
from serverless_ticketing_notifications.ticketing.domain.types import NonEmptyString
from pydantic import BaseModel, ConfigDict, Field


class Reservation(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    id: NonEmptyString
    user_id: NonEmptyString
    ticket_tier_id: NonEmptyString
    quantity: Annotated[int, Field(ge=1)]
    status: ReservationStatus
