from decimal import Decimal

import pytest
from pydantic import ValidationError

from serverless_ticketing_notifications.ticketing.domain.entity.ticket_tier import (
    TicketTier,
)


def make_ticket_tier(**overrides: object) -> TicketTier:
    data: dict[str, object] = {
        "id": "TICKET_TIER#01",
        "event_id": "EVENT#01",
        "name": "VIP",
        "base_price": Decimal("150.0"),
        "total_quantity": 1000,
        "available_quantity": 1000,
        "reserved_quantity": 0,
    }
    data.update(overrides)

    return TicketTier(**data)


class TestId:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(id="TICKET_TIER#01")

        assert ticket_tier.id is not None
        assert type(ticket_tier.id) is str
        assert ticket_tier.id == "TICKET_TIER#01"

    @pytest.mark.parametrize(
        "ticket_tier_id",
        [
            "TICKET_TIER#01       ",
            "       TICKET_TIER#01",
            "    TICKET_TIER#01   ",
        ],
    )
    def test_should_strip_id_surrounding_whitespace(self, ticket_tier_id: str) -> None:
        ticket_tier = make_ticket_tier(id=ticket_tier_id)

        assert ticket_tier.id is not None
        assert type(ticket_tier.id) is str
        assert ticket_tier.id == "TICKET_TIER#01"

    @pytest.mark.parametrize("ticket_tier_id", [True, 10, 1.0, object()])
    def test_should_reject_non_string_id(self, ticket_tier_id: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(id=ticket_tier_id)

    @pytest.mark.parametrize(
        "ticket_tier_id",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_id(self, ticket_tier_id: str) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(id=ticket_tier_id)


class TestEventId:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(event_id="EVENT#01")

        assert ticket_tier.event_id is not None
        assert type(ticket_tier.event_id) is str
        assert ticket_tier.event_id == "EVENT#01"

    @pytest.mark.parametrize(
        "event_id",
        [
            "EVENT#01       ",
            "       EVENT#01",
            "    EVENT#01   ",
        ],
    )
    def test_should_strip_id_surrounding_whitespace(self, event_id: str) -> None:
        ticket_tier = make_ticket_tier(event_id=event_id)

        assert ticket_tier.event_id is not None
        assert type(ticket_tier.event_id) is str
        assert ticket_tier.event_id == "EVENT#01"

    @pytest.mark.parametrize("event_id", [True, 10, 1.0])
    def test_should_reject_non_string_id(self, event_id: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(event_id=event_id)

    @pytest.mark.parametrize(
        "event_id",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_id(self, event_id: str) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(event_id=event_id)


class TestName:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(name="VIP")

        assert ticket_tier.name is not None
        assert type(ticket_tier.name) is str
        assert ticket_tier.name == "VIP"

    @pytest.mark.parametrize(
        "name",
        [
            "VIP       ",
            "       VIP",
            "    VIP   ",
        ],
    )
    def test_should_strip_name_surrounding_whitespace(self, name: str) -> None:
        ticket_tier = make_ticket_tier(name=name)

        assert ticket_tier.name is not None
        assert type(ticket_tier.name) is str
        assert ticket_tier.name == "VIP"

    @pytest.mark.parametrize(
        "name",
        [
            10,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_name(self, name: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(name=name)

    @pytest.mark.parametrize(
        "name",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_name(self, name: str) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(name=name)


class TestBasePrice:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(base_price=Decimal("150.0"))

        assert ticket_tier.base_price is not None
        assert type(ticket_tier.base_price) is Decimal
        assert ticket_tier.base_price == Decimal("150.0")

    def test_should_reject_negative_value(self) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(base_price=Decimal("-150.0"))

    @pytest.mark.parametrize(
        "base_price",
        [
            150.0,
            150,
            "150",
            object(),
        ],
    )
    def test_should_reject_non_decimal_value(self, base_price: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(base_price=base_price)


class TestTotalQuantity:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(total_quantity=1000)

        assert ticket_tier.total_quantity is not None
        assert type(ticket_tier.total_quantity) is int
        assert ticket_tier.total_quantity == 1000

    @pytest.mark.parametrize(
        "total_quantity",
        [
            0,
            -1,
            -1000,
        ],
    )
    def test_should_reject_invalid_value(self, total_quantity: int) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(
                total_quantity=total_quantity,
                available_quantity=0,
                reserved_quantity=0,
            )

    @pytest.mark.parametrize(
        "total_quantity",
        [
            1000.0,
            "1000",
            object(),
        ],
    )
    def test_should_reject_non_integer_value(self, total_quantity: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(total_quantity=total_quantity)


class TestAvailableQuantity:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(available_quantity=1000)

        assert ticket_tier.available_quantity is not None
        assert type(ticket_tier.available_quantity) is int
        assert ticket_tier.available_quantity == 1000

    def test_should_reject_negative_value(self) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(available_quantity=-1000)

    @pytest.mark.parametrize(
        "available_quantity",
        [
            1000.0,
            "1000",
            object(),
        ],
    )
    def test_should_reject_non_integer_value(self, available_quantity: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(available_quantity=available_quantity)

    def test_should_reject_value_greater_than_total_quantity(self) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(
                total_quantity=1000,
                available_quantity=1001,
                reserved_quantity=0,
            )


class TestReservedQuantity:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = make_ticket_tier(reserved_quantity=10)

        assert ticket_tier.reserved_quantity is not None
        assert type(ticket_tier.reserved_quantity) is int
        assert ticket_tier.reserved_quantity == 10

    def test_should_reject_negative_value(self) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(reserved_quantity=-1)

    @pytest.mark.parametrize(
        "reserved_quantity",
        [
            1000.0,
            "1000",
            object(),
        ],
    )
    def test_should_reject_non_integer_value(self, reserved_quantity: object) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(reserved_quantity=reserved_quantity)

    def test_should_reject_value_greater_than_available_quantity(self) -> None:
        with pytest.raises(ValidationError):
            make_ticket_tier(
                total_quantity=1000,
                available_quantity=10,
                reserved_quantity=11,
            )


class TestCalculatedQuantities:
    def test_should_calculate_sold_quantity(self) -> None:
        ticket_tier = make_ticket_tier(
            total_quantity=1000,
            available_quantity=900,
            reserved_quantity=100,
        )

        assert ticket_tier.sold_quantity == 100

    def test_should_calculate_reservable_quantity(self) -> None:
        ticket_tier = make_ticket_tier(
            total_quantity=1000,
            available_quantity=900,
            reserved_quantity=100,
        )

        assert ticket_tier.reservable_quantity == 800
