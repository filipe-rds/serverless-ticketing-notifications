from aws_lambda_powertools.event_handler.router import APIGatewayRouter

from serverless_ticketing_notifications.common.response_entity import ResponseEntity

router = APIGatewayRouter()


@router.get("/events")
def get_events():
    return ResponseEntity.ok(message="Public event listing route is running!", data=[])


@router.get("/events/<event_id>/tickets")
def get_event_tickets(event_id: str):
    return ResponseEntity.ok(
        message="Public event tickets route is running!",
        data={"event_id": event_id},
    )


@router.post("/events/<event_id>/reservations")
def create_event_reservation(event_id: str):
    return ResponseEntity.created(
        message="Reservation creation route is running!",
        data={"event_id": event_id},
    )


@router.post("/reservations/<reservation_id>/checkout")
def create_reservation_checkout(reservation_id: str):
    return ResponseEntity.ok(
        message="Reservation checkout route is running!",
        data={"reservation_id": reservation_id},
    )
