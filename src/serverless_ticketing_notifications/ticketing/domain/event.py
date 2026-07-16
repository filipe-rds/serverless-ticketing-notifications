from pydantic import BaseModel, ConfigDict

from serverless_ticketing_notifications.ticketing.domain.types import NonEmptyString


class Event(BaseModel):
    model_config = ConfigDict(strict=True)

    id: NonEmptyString
    name: NonEmptyString
