from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Notification:
    notification_id: UUID
    user_id: UUID
    type: int
    destination: str
    status: str
    message_body: str
