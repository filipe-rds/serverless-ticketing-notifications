import json

from aws_lambda_powertools.event_handler.router import APIGatewayRouter

router = APIGatewayRouter()


@router.get("/events/<event_id>")
def get_event(event_id: str):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "controller": "Customer",
                "message": "Customer controller is running!",
                "route": f"/events/{event_id}",
            }
        ),
    }


@router.post("/events")
def create_event():
    pass


@router.patch("/events/<event_id>")
def update_event(event_id: str, event: dict):
    pass


@router.delete("/events/<event_id>")
def remove_event(event_id: str):
    pass


@router.get("/events")
def list_events():
    pass
