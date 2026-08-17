from datetime import datetime
from zoneinfo import ZoneInfo


class DateTime(datetime):
    _FORMAT = "%Y-%m-%d%H:%M:%S"
    _TIMEZONE = ZoneInfo("America/Sao_Paulo")

    def __new__(cls, value: str) -> datetime:
        try:
            dt = datetime.strptime(value, cls._FORMAT).replace(tzinfo=cls._TIMEZONE)
        except ValueError:
            raise ValueError(f"Invalid datetime format. Expected: {cls._FORMAT}")

        return super().__new__(
            cls,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            tzinfo=cls._TIMEZONE,
        )

    @classmethod
    def future(cls, value: str) -> datetime:
        instance = cls(value)

        if instance <= datetime.now(tz=cls._TIMEZONE):
            raise ValueError("Must be a future datetime")

        return instance

    @classmethod
    def past(cls, value: str) -> datetime:
        instance = cls(value)

        if instance > datetime.now(tz=cls._TIMEZONE):
            raise ValueError("Must be a past datetime")

        return instance
