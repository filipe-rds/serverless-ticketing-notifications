class NonNegativeInteger(int):
    def __new__(cls, value: int) -> int:
        if not type(value) is int:
            raise TypeError("Expected a integer.")

        if type(value) is int and value < 0:
            raise ValueError("Expected a non-negative integer.")

        return int.__new__(cls, value)
