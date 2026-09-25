from dataclasses import dataclass
from uuid import UUID

from ticketstream.notifications.domain.enumerators.notification_status import (
    NotificationStatus,
)
from ticketstream.notifications.domain.enumerators.notification_type import (
    NotificationType,
)


@dataclass(frozen=True, slots=True)
class Notification:
    notification_id: UUID
    user_id: UUID
    type: NotificationType
    destination: str
    status: NotificationStatus
    message_body: str
