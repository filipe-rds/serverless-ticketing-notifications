from pydantic import BaseModel, ConfigDict

from serverless_ticketing_notifications.ticketing.domain.type.non_empty_string import (
    NonEmptyString,
)


class Event(BaseModel):
    model_config = ConfigDict(strict=True)

    id: NonEmptyString
    name: NonEmptyString
    description: NonEmptyString