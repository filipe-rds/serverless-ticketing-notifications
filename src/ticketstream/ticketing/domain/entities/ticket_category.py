from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class TicketCategory:
    ticket_category_id: str
    event_id: str
    name: str
    base_price: Decimal
    total_quantity: int
    available_quantity: int
    reserved_quantity: int

    def __post_init__(self) -> None:
        if not self.ticket_category_id.strip():
            raise ValueError("Ticket category id cannot be empty")

        if not self.event_id.strip():
            raise ValueError("Event id cannot be empty")

        if not self.name.strip():
            raise ValueError("Name cannot be empty")

        if self.base_price <= 0:
            raise ValueError("Base price must be greater than zero")

        if self.total_quantity <= 0:
            raise ValueError("Total quantity must be greater than zero")

        if self.available_quantity > self.total_quantity:
            raise ValueError("Available quantity cannot exceed total quantity")

        if self.reserved_quantity > self.available_quantity:
            raise ValueError("Reserved quantity cannot exceed available quantity")

    @property
    def sold_quantity(self) -> int:
        return self.total_quantity - self.available_quantity

    @property
    def reservable_quantity(self) -> int:
        return self.available_quantity - self.reserved_quantity

    def update(self, **changes: Any) -> TicketCategory:
        valid_fields = {
            "name",
            "base_price",
            "total_quantity",
            "available_quantity",
            "reserved_quantity",
        }

        unknown_fields = set(changes) - valid_fields

        if unknown_fields:
            raise ValueError(
                f"Unknown fields for update: {', '.join(sorted(unknown_fields))}"
            )

        return replace(self, **changes)
