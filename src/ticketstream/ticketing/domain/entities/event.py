from datetime import datetime


class Event:
    def __init__(
        self,
        event_id: str,
        name: str,
        description: str,
        starts_at: datetime,
        ends_at: datetime,
    ) -> None:
        self._event_id = event_id
        self._name = name
        self._description = description
        self._starts_at = starts_at
        self._ends_at = ends_at

    @property
    def event_id(self) -> str:
        return self.event_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def starts_at(self) -> datetime:
        return self._starts_at

    @property
    def ends_at(self) -> datetime:
        return self._ends_at
