from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TicketCategory:
    ticket_category_id: UUID
    name: str
    base_price: Decimal
    capacity: int
    reserved: int
    sold: int

    @property
    def reservable(self) -> int:
        return self.capacity - self.sold - self.reserved
