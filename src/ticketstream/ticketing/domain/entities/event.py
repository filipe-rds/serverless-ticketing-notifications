from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Event:
    event_id: str
    name: str
    description: str
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self):

        if not self.event_id.strip():
            raise ValueError("Event id cannot be empty")

        if self.name.strip() == "":
            raise ValueError("Event name cannot be empty")

        if self.description.strip() == "":
            raise ValueError("Event description cannot be empty")

        if not self.starts_at:
            raise ValueError("Event starts_at cannot be empty")

        if not self.ends_at:
            raise ValueError("Event ends_at cannot be empty")

    def update(self, **changes: Any) -> Event:
        valid_fields = {"name", "description", "starts_at", "ends_at"}

        unknown_fields = set(changes) - valid_fields

        if unknown_fields:
            raise ValueError(
                f"Unknown fields for update: {', '.join(sorted(unknown_fields))}"
            )

        return replace(self, **changes)
