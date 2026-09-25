from collections.abc import Callable

import pytest

from ticketstream.ticketing.domain.entities.ticket_category import TicketCategory


@pytest.mark.parametrize(
    ("capacity", "reserved", "sold", "expected"),
    [
        (50, 0, 0, 50),  # nada tomado
        (50, 5, 10, 35),  # reserva e venda coexistindo
        (50, 20, 30, 0),  # lotado por reserva + venda
        (50, 50, 0, 0),  # lotado so por reservas PENDING
        (50, 0, 50, 0),  # lotado so por vendas CONFIRMED
    ],
)
def test_reservable_discounts_reserved_and_sold_from_capacity(
    make_ticket_category: Callable[..., TicketCategory],
    capacity: int,
    reserved: int,
    sold: int,
    expected: int,
) -> None:
    category = make_ticket_category(capacity=capacity, reserved=reserved, sold=sold)

    assert category.reservable == expected
