from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, model_validator
from decimal import Decimal

from serverless_ticketing_notifications.ticketing.domain.type.non_empty_string import (
    NonEmptyString,
)


class TicketTier(BaseModel):
    model_config = ConfigDict(strict=True)

    id: NonEmptyString
    event_id: NonEmptyString
    name: NonEmptyString
    base_price: Annotated[Decimal, Field(ge=0)]
    total_quantity: Annotated[int, Field(ge=1)]
    available_quantity: Annotated[
        int, Field(ge=0)
    ]  # The number of tickets available for sale
    reserved_quantity: Annotated[
        int, Field(ge=0)
    ]  # The number of tickets that are reserved but not yet confirmed

    @property
    def sold_quantity(self) -> int:
        return self.total_quantity - self.available_quantity

    @property
    def reservable_quantity(self) -> int:
        return self.available_quantity - self.reserved_quantity

    @model_validator(mode="after")
    def validate_quantities(self) -> "TicketTier":
        if self.available_quantity > self.total_quantity:
            raise ValueError(
                "Available quantity must be less than or equal to total quantity."
            )

        elif self.reserved_quantity > self.available_quantity:
            raise ValueError(
                "Reserved quantity must be less than or equal to available quantity."
            )

        return self
