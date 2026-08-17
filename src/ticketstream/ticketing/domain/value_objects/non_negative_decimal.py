from decimal import Decimal


class NonNegativeDecimal(Decimal):
    def __new__(cls, value: Decimal):
        if type(value) is not Decimal:
            raise TypeError("Expected a Decimal.")

        if value < Decimal("0"):
            raise ValueError("Expected a non-negative value.")

        return super().__new__(cls, value)
