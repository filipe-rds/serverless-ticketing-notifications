from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

from serverless_ticketing_notifications.ticketing.domain.constraints import (
    NonEmptyString,
)


class TicketTier(BaseModel):
    model_config = ConfigDict(strict=True)

    id: NonEmptyString
    event_id: NonEmptyString
    name: NonEmptyString
    base_price: Annotated[Decimal, Field(ge=0)]
    available_quantity: Annotated[int, Field(ge=0)]
