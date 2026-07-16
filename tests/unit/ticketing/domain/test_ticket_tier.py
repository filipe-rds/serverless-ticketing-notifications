from pydantic import ValidationError
from decimal import Decimal
from serverless_ticketing_notifications.ticketing.domain.ticket_tier import TicketTier
import pytest


class TestId:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id="EVENT#01",
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

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
        ticket_tier = TicketTier(
            id=ticket_tier_id,
            event_id="EVENT#01",
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

        assert ticket_tier.id is not None
        assert type(ticket_tier.id) is str
        assert ticket_tier.id == "TICKET_TIER#01"

    @pytest.mark.parametrize("ticket_tier_id", [True, 10, 1.0, object()])
    def test_should_reject_non_string_id(self, ticket_tier_id: object) -> None:
        with pytest.raises(ValidationError):
            TicketTier(
                id=ticket_tier_id,  # ty:ignore[invalid-argument-type]
                event_id="EVENT#01",
                name="VIP",
                base_price=Decimal(150.0),
                available_quantity=1000,
            )

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
            TicketTier(
                id=ticket_tier_id,
                event_id="EVENT#01",
                name="VIP",
                base_price=Decimal(150.0),
                available_quantity=1000,
            )


class TestEventId:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id="EVENT#01",
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

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
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id=event_id,
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

        assert ticket_tier.event_id is not None
        assert type(ticket_tier.event_id) is str
        assert ticket_tier.event_id == "EVENT#01"

    @pytest.mark.parametrize("event_id", [True, 10, 1.0])
    def test_should_reject_non_string_id(self, event_id: object) -> None:
        with pytest.raises(ValidationError):
            TicketTier(
                id="TICKET_TIER#01",
                event_id=event_id,  # ty:ignore[invalid-argument-type]
                name="VIP",
                base_price=Decimal(150.0),
                available_quantity=1000,
            )

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
            TicketTier(
                id="TICKET_TIER#01",
                event_id=event_id,
                name="VIP",
                base_price=Decimal(150.0),
                available_quantity=1000,
            )


class TestName:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id="EVENT#01",
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

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
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id="EVENT#01",
            name=name,
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

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
            TicketTier(
                id="TICKET_TIER#01",
                event_id="EVENT#01",
                name=name,  # ty:ignore[invalid-argument-type]
                base_price=Decimal(150.0),
                available_quantity=1000,
            )

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
            TicketTier(
                id="TICKET_TIER#01",
                event_id="EVENT#01",
                name=name,
                base_price=Decimal(150.0),
                available_quantity=1000,
            )


class TestBasePrice:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id="EVENT#01",
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

        assert ticket_tier.base_price is not None
        assert type(ticket_tier.base_price) is Decimal
        assert ticket_tier.base_price == Decimal(150.0)

    def test_should_reject_negative_value(self) -> None:
        with pytest.raises(ValidationError):
            TicketTier(
                id="TICKET_TIER#01",
                event_id="EVENT#01",
                name="VIP",
                base_price=Decimal(-150.0),
                available_quantity=1000,
            )

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
            TicketTier(
                id="TICKET_TIER#01",
                event_id="EVENT#01",
                name="VIP",
                base_price=base_price,  # ty:ignore[invalid-argument-type]
                available_quantity=1000,
            )


class TestAvailableQuantity:
    def test_should_store_expected_value(self) -> None:
        ticket_tier = TicketTier(
            id="TICKET_TIER#01",
            event_id="EVENT#01",
            name="VIP",
            base_price=Decimal(150.0),
            available_quantity=1000,
        )

        assert ticket_tier.available_quantity is not None
        assert type(ticket_tier.available_quantity) is int
        assert ticket_tier.available_quantity == 1000

    def test_should_reject_negative_value(self) -> None:
        with pytest.raises(ValidationError):
            TicketTier(
                id="TICKET_TIER#01",
                event_id="EVENT#01",
                name="VIP",
                base_price=Decimal(150.0),
                available_quantity=-1000,
            )

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
            TicketTier(
                id="TICKET_TIER#01",
                event_id="EVENT#01",
                name="VIP",
                base_price=Decimal(150.0),
                available_quantity=available_quantity,  # ty:ignore[invalid-argument-type]
            )
