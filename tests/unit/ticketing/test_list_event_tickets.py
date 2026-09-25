from collections.abc import Callable
from decimal import Decimal
from uuid import uuid4

import pytest

from ticketstream.shared.result import Err, Ok
from ticketstream.ticketing.application.errors import EventNotFound
from ticketstream.ticketing.application.ports import EventRepositoryPort
from ticketstream.ticketing.application.use_cases.list_event_tickets.request import (
    ListEventTicketsRequest,
)
from ticketstream.ticketing.application.use_cases.list_event_tickets.use_case import (
    ListEventTicketsUseCase,
)
from ticketstream.ticketing.domain.entities.event import Event
from ticketstream.ticketing.domain.entities.ticket_category import TicketCategory


def test_returns_the_categories_and_prices_of_the_requested_event(
    make_event: Callable[..., Event],
    make_ticket_category: Callable[..., TicketCategory],
    make_event_repository: Callable[..., EventRepositoryPort],
) -> None:
    wanted = make_event(
        categories=(
            make_ticket_category(name="Camarote", base_price=Decimal("250.00")),
            make_ticket_category(name="Pista", base_price=Decimal("120.00")),
        )
    )
    other = make_event(categories=(make_ticket_category(name="Backstage"),))
    use_case = ListEventTicketsUseCase(make_event_repository(other, wanted))

    match use_case.execute(ListEventTicketsRequest(event_id=wanted.event_id)):
        case Ok(response):
            assert response.event_id == wanted.event_id
            assert [
                (category.name, category.base_price) for category in response.categories
            ] == [("Camarote", Decimal("250.00")), ("Pista", Decimal("120.00"))]
        case Err(error):
            pytest.fail(f"esperava Ok, veio Err({error})")


def test_returns_no_categories_when_the_event_has_none(
    make_event: Callable[..., Event],
    make_event_repository: Callable[..., EventRepositoryPort],
) -> None:
    event = make_event(categories=())
    use_case = ListEventTicketsUseCase(make_event_repository(event))

    match use_case.execute(ListEventTicketsRequest(event_id=event.event_id)):
        case Ok(response):
            assert response.categories == ()
        case Err(error):
            pytest.fail(f"evento sem categoria e Ok vazio, nao Err({error})")


def test_returns_event_not_found_carrying_the_requested_id(
    make_event: Callable[..., Event],
    make_event_repository: Callable[..., EventRepositoryPort],
) -> None:
    unknown_event_id = uuid4()
    use_case = ListEventTicketsUseCase(make_event_repository(make_event()))

    match use_case.execute(ListEventTicketsRequest(event_id=unknown_event_id)):
        case Err(EventNotFound() as error):
            assert error.event_id == unknown_event_id
        case other:
            pytest.fail(f"esperava Err(EventNotFound), veio {other}")
