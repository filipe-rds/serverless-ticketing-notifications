from aws_lambda_powertools.event_handler.router import APIGatewayRouter

router = APIGatewayRouter()


@router.get("/events")
def get_events():
    pass


@router.get("/events/<event_id>/tickets")
def get_event_tickets(event_id: str):
    pass


@router.post("/events/<event_id>/reservations")
def create_event_reservation(event_id: str):
    pass


@router.post("/reservations/<reservation_id>/checkout")
def create_reservation_checkout(reservation_id: str):
    pass
