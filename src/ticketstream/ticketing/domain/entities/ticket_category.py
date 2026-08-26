from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TicketCategory:
    ticket_category_id: UUID
    name: str
    base_price: Decimal
    total_quantity: int
    available_quantity: int
    reserved_quantity: int

    @property
    def reservable_quantity(self) -> int:
        return self.available_quantity - self.reserved_quantity
