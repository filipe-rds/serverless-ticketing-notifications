from decimal import Decimal


class TicketCategory:
    def __init__(
        self,
        ticket_category_id: str,
        name: str,
        base_price: Decimal,
        total_quantity: int,
        available_quantity: int,
        reserved_quantity: int,
    ) -> None:
        self._id = ticket_category_id
        self._name = name
        self._base_price = base_price
        self._total_quantity = total_quantity
        self._available_quantity = available_quantity
        self._reserved_quantity = reserved_quantity

        self._validate_quantities()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def base_price(self) -> Decimal:
        return self._base_price

    @property
    def total_quantity(self) -> int:
        return self._total_quantity

    @total_quantity.setter
    def total_quantity(self, value: int) -> None:
        self._total_quantity = self._validate_total_quantity(value)

    @property
    def available_quantity(self) -> int:
        return self._available_quantity

    @available_quantity.setter
    def available_quantity(self, value: int) -> None:
        self._available_quantity = self._validate_available_quantity(value)

    @property
    def reserved_quantity(self) -> int:
        return self._reserved_quantity

    @reserved_quantity.setter
    def reserved_quantity(self, value: int) -> None:
        self._reserved_quantity = self._validate_reserved_quantity(value)

    @property
    def sold_quantity(self) -> int:
        return self._total_quantity - self._available_quantity

    @property
    def reservable_quantity(self) -> int:
        return self._available_quantity - self._reserved_quantity

    def _validate_quantities(self) -> None:
        self._validate_total_quantity(self._total_quantity)
        self._validate_available_quantity(self._available_quantity)
        self._validate_reserved_quantity(self._reserved_quantity)

    def _validate_available_quantity(self, value: int) -> int:
        if value > self._total_quantity:
            raise ValueError(
                "Available quantity must be less than or equal to total quantity."
            )

        return value

    def _validate_reserved_quantity(self, value: int) -> int:
        if value > self._available_quantity:
            raise ValueError(
                "Reserved quantity must be less than or equal to available quantity."
            )

        return value

    def _validate_total_quantity(self, value: int) -> int:
        diference = value - self._total_quantity

        if diference < self.reservable_quantity:
            raise ValueError(
                "Total quantity exceeds the reservable limit given available and reserved quantities."
            )

        return value
