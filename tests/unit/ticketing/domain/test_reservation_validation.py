import pytest
from pydantic import ValidationError

from serverless_ticketing_notifications.ticketing.domain.entity.reservation import (
    Reservation,
    ReservationStatus,
)


def make_reservation(**overrides: object) -> Reservation:
    data: dict[str, object] = {
        "id": "RESERVATION#01",
        "user_id": "USER#01",
        "event_id": "EVENT#01",
        "ticket_category_id": "TICKET_CATEGORY#01",
        "quantity": 1,
        "status": ReservationStatus.PENDING,
    }
    data.update(overrides)

    return Reservation(**data)


class TestId:
    def test_should_store_expected_value(self) -> None:
        reservation = make_reservation(id="RESERVATION#01")

        assert reservation.id is not None
        assert type(reservation.id) is str
        assert reservation.id == "RESERVATION#01"

    @pytest.mark.parametrize(
        "reservation_id",
        [
            "RESERVATION#01       ",
            "       RESERVATION#01",
            "    RESERVATION#01   ",
        ],
    )
    def test_should_strip_id_surrounding_whitespace(
        self,
        reservation_id: str,
    ) -> None:
        reservation = make_reservation(id=reservation_id)

        assert reservation.id == "RESERVATION#01"

    @pytest.mark.parametrize("reservation_id", [True, 10, 1.0, object()])
    def test_should_reject_non_string_id(
        self,
        reservation_id: object,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(id=reservation_id)

    @pytest.mark.parametrize("reservation_id", ["", " ", "   "])
    def test_should_reject_invalid_string_id(
        self,
        reservation_id: str,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(id=reservation_id)


class TestUserId:
    def test_should_store_expected_value(self) -> None:
        reservation = make_reservation(user_id="USER#01")

        assert reservation.user_id is not None
        assert type(reservation.user_id) is str
        assert reservation.user_id == "USER#01"

    @pytest.mark.parametrize(
        "user_id",
        [
            "USER#01       ",
            "       USER#01",
            "    USER#01   ",
        ],
    )
    def test_should_strip_user_id_surrounding_whitespace(
        self,
        user_id: str,
    ) -> None:
        reservation = make_reservation(user_id=user_id)

        assert reservation.user_id == "USER#01"

    @pytest.mark.parametrize("user_id", [True, 10, 1.0, object()])
    def test_should_reject_non_string_user_id(
        self,
        user_id: object,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(user_id=user_id)

    @pytest.mark.parametrize("user_id", ["", " ", "   "])
    def test_should_reject_invalid_string_user_id(
        self,
        user_id: str,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(user_id=user_id)


class TestEventId:
    def test_should_store_expected_value(self) -> None:
        reservation = make_reservation(event_id="EVENT#01")

        assert reservation.event_id is not None
        assert type(reservation.event_id) is str
        assert reservation.event_id == "EVENT#01"

    @pytest.mark.parametrize(
        "event_id",
        [
            "EVENT#01       ",
            "       EVENT#01",
            "    EVENT#01   ",
        ],
    )
    def test_should_strip_event_id_surrounding_whitespace(
        self,
        event_id: str,
    ) -> None:
        reservation = make_reservation(event_id=event_id)

        assert reservation.event_id == "EVENT#01"

    @pytest.mark.parametrize("event_id", [True, 10, 1.0, object()])
    def test_should_reject_non_string_event_id(
        self,
        event_id: object,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(event_id=event_id)

    @pytest.mark.parametrize("event_id", ["", " ", "   "])
    def test_should_reject_invalid_string_event_id(
        self,
        event_id: str,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(event_id=event_id)


class TestTicketCategoryId:
    def test_should_store_expected_value(self) -> None:
        reservation = make_reservation(ticket_category_id="TICKET_CATEGORY#01")

        assert reservation.ticket_category_id is not None
        assert type(reservation.ticket_category_id) is str
        assert reservation.ticket_category_id == "TICKET_CATEGORY#01"

    @pytest.mark.parametrize(
        "ticket_category_id",
        [
            "TICKET_CATEGORY#01       ",
            "       TICKET_CATEGORY#01",
            "    TICKET_CATEGORY#01   ",
        ],
    )
    def test_should_strip_ticket_category_id_surrounding_whitespace(
        self,
        ticket_category_id: str,
    ) -> None:
        reservation = make_reservation(ticket_category_id=ticket_category_id)

        assert reservation.ticket_category_id == "TICKET_CATEGORY#01"

    @pytest.mark.parametrize("ticket_category_id", [True, 10, 1.0, object()])
    def test_should_reject_non_string_ticket_category_id(
        self,
        ticket_category_id: object,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(ticket_category_id=ticket_category_id)

    @pytest.mark.parametrize("ticket_category_id", ["", " ", "   "])
    def test_should_reject_invalid_string_ticket_category_id(
        self,
        ticket_category_id: str,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(ticket_category_id=ticket_category_id)


class TestQuantity:
    def test_should_store_expected_value(self) -> None:
        reservation = make_reservation(quantity=2)

        assert reservation.quantity is not None
        assert type(reservation.quantity) is int
        assert reservation.quantity == 2

    @pytest.mark.parametrize("quantity", [True, 1.0, "1", object()])
    def test_should_reject_quantity_when_not_integer(
        self,
        quantity: object,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(quantity=quantity)

    @pytest.mark.parametrize("quantity", [0, -1, -10])
    def test_should_reject_quantity_when_less_than_one(
        self,
        quantity: int,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(quantity=quantity)


class TestStatus:
    def test_should_store_expected_value(self) -> None:
        reservation = make_reservation(status=ReservationStatus.PENDING)

        assert reservation.status is not None
        assert type(reservation.status) is ReservationStatus
        assert reservation.status is ReservationStatus.PENDING

    @pytest.mark.parametrize("status", ["PENDING", True, 1, object()])
    def test_should_reject_invalid_status(
        self,
        status: object,
    ) -> None:
        with pytest.raises(ValidationError):
            make_reservation(status=status)
