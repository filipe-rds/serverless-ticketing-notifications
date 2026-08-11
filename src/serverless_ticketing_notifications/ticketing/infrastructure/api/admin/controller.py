from aws_lambda_powertools.event_handler.router import APIGatewayRouter

from serverless_ticketing_notifications.ticketing.infrastructure.view.response_entity import (
    ResponseEntity,
)


router = APIGatewayRouter()


@router.get("/events/<event_id>")
def get_event(event_id: str):
    return ResponseEntity.ok(
        message="Get event route is running!", data={"event_id": event_id}
    )


@router.post("/events")
def create_event():
    return ResponseEntity.created(message="Event creation route is running!")


@router.patch("/events/<event_id>")
def update_event(event_id: str):
    return ResponseEntity.ok(
        message="Event update route is running!",
        data={"event_id": event_id},
    )


@router.delete("/events/<event_id>")
def remove_event(event_id: str):
    return ResponseEntity.ok(
        message="Event removal route is running!",
        data={"event_id": event_id},
    )


@router.get("/events")
def list_events():
    return ResponseEntity.ok(message="Event listing route is running!", data=[])
