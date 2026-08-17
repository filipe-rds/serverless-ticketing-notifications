from ticketstream.shared.domain.value_objects.date_time import DateTime
from ticketstream.shared.domain.value_objects.non_empty_string import NonEmptyString


class Event:
    def __init__(
        self,
        id: NonEmptyString,
        name: NonEmptyString,
        description: NonEmptyString,
        starts_at: DateTime,
        ends_at: DateTime,
    ) -> None:
        self._id = id
        self._name = name
        self._description = description
        self._starts_at = starts_at
        self._ends_at = ends_at

    @property
    def id(self) -> NonEmptyString:
        return self._id

    @property
    def name(self) -> NonEmptyString:
        return self._name

    @property
    def description(self) -> NonEmptyString:
        return self._description

    @property
    def starts_at(self) -> DateTime:
        return self._starts_at

    @property
    def ends_at(self) -> DateTime:
        return self._ends_at
