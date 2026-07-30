from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter

tracer = Tracer()
router = APIGatewayRouter()

@router.get("/events/<event_id>")
@tracer.capture_method
def get_event(event_id: str):
    pass

@router.post("/events")
@tracer.capture_method
def create_event(event: dict):
    pass

@router.patch("/events/<event_id>")
@tracer.capture_method
def update_event(event_id: str, event: dict):
    pass

@router.delete("/events/<event_id>")
@tracer.capture_method
def remove_event(event_id: str):
    pass

@router.get("/events")
@tracer.capture_method
def list_events():
    pass