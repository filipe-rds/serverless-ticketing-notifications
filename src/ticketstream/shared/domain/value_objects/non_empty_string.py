class NonEmptyString(str):
    def __new__(cls, value: str) -> str:
        if type(value) is not str:
            raise TypeError("Expected a string.")

        if type(value) is str and len(value.strip()) == 0:
            raise ValueError("Expected a non-empty string.")

        return super().__new__(cls, value)
