from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from tests.fakes.in_memory_event_repository import InMemoryEventRepository
from ticketstream.ticketing.application.ports import EventRepositoryPort
from ticketstream.ticketing.domain.entities.event import Event
from ticketstream.ticketing.domain.entities.ticket_category import TicketCategory


@pytest.fixture
def make_ticket_category() -> Callable[..., TicketCategory]:
    def _make(
        *,
        name: str = "Camarote",
        base_price: Decimal = Decimal("250.00"),
        capacity: int = 50,
        reserved: int = 0,
        sold: int = 0,
        ticket_category_id: UUID | None = None,
    ) -> TicketCategory:
        return TicketCategory(
            ticket_category_id=ticket_category_id or uuid4(),
            name=name,
            base_price=base_price,
            capacity=capacity,
            reserved=reserved,
            sold=sold,
        )

    return _make


@pytest.fixture
def make_event() -> Callable[..., Event]:
    def _make(
        *,
        event_id: UUID | None = None,
        name: str = "Tech Conference 2026",
        categories: tuple[TicketCategory, ...] = (),
        max_tickets_per_user: int = 4,
    ) -> Event:
        start_at = datetime.now(UTC)

        return Event(
            event_id=event_id or uuid4(),
            name=name,
            description="Conferencia anual",
            location="Sao Paulo",
            max_tickets_per_user=max_tickets_per_user,
            categories=categories,
            start_at=start_at,
            end_at=start_at + timedelta(hours=8),
        )

    return _make


@pytest.fixture
def make_event_repository() -> Callable[..., EventRepositoryPort]:
    def _make(*events: Event) -> EventRepositoryPort:
        return InMemoryEventRepository(list(events))

    return _make
