import pytest

from serverless_ticketing_notifications.ticketing.domain.enums import (
    ReservationStatus,
)
from serverless_ticketing_notifications.ticketing.domain.reservation import (
    Reservation,
)


class TestId:
    def test_should_store_expected_value(self) -> None:
        reservation = Reservation(
            id="RESERVATION#01",
            user_id="USER#01",
            ticket_tier_id="TICKET_TIER#01",
            quantity=1,
            status=ReservationStatus.PENDING,
        )

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
        reservation = Reservation(
            id=reservation_id,
            user_id="USER#01",
            ticket_tier_id="TICKET_TIER#01",
            quantity=1,
            status=ReservationStatus.PENDING,
        )

        assert reservation.id == "RESERVATION#01"

    @pytest.mark.parametrize(
        "reservation_id",
        [
            True,
            10,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_id(
        self,
        reservation_id: object,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id=reservation_id,  # ty:ignore[invalid-argument-type]
                user_id="USER#01",
                ticket_tier_id="TICKET_TIER#01",
                quantity=1,
                status=ReservationStatus.PENDING,
            )

    @pytest.mark.parametrize(
        "reservation_id",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_id(
        self,
        reservation_id: str,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id=reservation_id,
                user_id="USER#01",
                ticket_tier_id="TICKET_TIER#01",
                quantity=1,
                status=ReservationStatus.PENDING,
            )


class TestUserId:
    def test_should_store_expected_value(self) -> None:
        reservation = Reservation(
            id="RESERVATION#01",
            user_id="USER#01",
            ticket_tier_id="TICKET_TIER#01",
            quantity=1,
            status=ReservationStatus.PENDING,
        )

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
        reservation = Reservation(
            id="RESERVATION#01",
            user_id=user_id,
            ticket_tier_id="TICKET_TIER#01",
            quantity=1,
            status=ReservationStatus.PENDING,
        )

        assert reservation.user_id == "USER#01"

    @pytest.mark.parametrize(
        "user_id",
        [
            True,
            10,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_user_id(
        self,
        user_id: object,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id=user_id,  # ty:ignore[invalid-argument-type]
                ticket_tier_id="TICKET_TIER#01",
                quantity=1,
                status=ReservationStatus.PENDING,
            )

    @pytest.mark.parametrize(
        "user_id",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_user_id(
        self,
        user_id: str,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id=user_id,
                ticket_tier_id="TICKET_TIER#01",
                quantity=1,
                status=ReservationStatus.PENDING,
            )


class TestTicketTierId:
    def test_should_store_expected_value(self) -> None:
        reservation = Reservation(
            id="RESERVATION#01",
            user_id="USER#01",
            ticket_tier_id="TICKET_TIER#01",
            quantity=1,
            status=ReservationStatus.PENDING,
        )

        assert reservation.ticket_tier_id is not None
        assert type(reservation.ticket_tier_id) is str
        assert reservation.ticket_tier_id == "TICKET_TIER#01"

    @pytest.mark.parametrize(
        "ticket_tier_id",
        [
            "TICKET_TIER#01       ",
            "       TICKET_TIER#01",
            "    TICKET_TIER#01   ",
        ],
    )
    def test_should_strip_ticket_tier_id_surrounding_whitespace(
        self,
        ticket_tier_id: str,
    ) -> None:
        reservation = Reservation(
            id="RESERVATION#01",
            user_id="USER#01",
            ticket_tier_id=ticket_tier_id,
            quantity=1,
            status=ReservationStatus.PENDING,
        )

        assert reservation.ticket_tier_id == "TICKET_TIER#01"

    @pytest.mark.parametrize(
        "ticket_tier_id",
        [
            True,
            10,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_ticket_tier_id(
        self,
        ticket_tier_id: object,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id="USER#01",
                ticket_tier_id=ticket_tier_id,  # ty:ignore[invalid-argument-type]
                quantity=1,
                status=ReservationStatus.PENDING,
            )

    @pytest.mark.parametrize(
        "ticket_tier_id",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_ticket_tier_id(
        self,
        ticket_tier_id: str,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id="USER#01",
                ticket_tier_id=ticket_tier_id,
                quantity=1,
                status=ReservationStatus.PENDING,
            )


class TestQuantity:
    def test_should_store_expected_value(self) -> None:
        reservation = Reservation(
            id="RESERVATION#01",
            user_id="USER#01",
            ticket_tier_id="TICKET_TIER#01",
            quantity=2,
            status=ReservationStatus.PENDING,
        )

        assert reservation.quantity is not None
        assert type(reservation.quantity) is int
        assert reservation.quantity == 2

    @pytest.mark.parametrize(
        "quantity",
        [
            True,
            1.0,
            "1",
            object(),
        ],
    )
    def test_should_reject_quantity_when_not_integer(
        self,
        quantity: object,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id="USER#01",
                ticket_tier_id="TICKET_TIER#01",
                quantity=quantity,  # ty:ignore[invalid-argument-type]
                status=ReservationStatus.PENDING,
            )

    @pytest.mark.parametrize(
        "quantity",
        [
            0,
            -1,
            -10,
        ],
    )
    def test_should_reject_quantity_when_less_than_one(
        self,
        quantity: int,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id="USER#01",
                ticket_tier_id="TICKET_TIER#01",
                quantity=quantity,
                status=ReservationStatus.PENDING,
            )


class TestStatus:
    def test_should_store_expected_value(self) -> None:
        reservation = Reservation(
            id="RESERVATION#01",
            user_id="USER#01",
            ticket_tier_id="TICKET_TIER#01",
            quantity=1,
            status=ReservationStatus.PENDING,
        )

        assert reservation.status is not None
        assert type(reservation.status) is ReservationStatus
        assert reservation.status is ReservationStatus.PENDING

    @pytest.mark.parametrize(
        "status",
        [
            "PENDING",
            True,
            1,
            object(),
        ],
    )
    def test_should_reject_invalid_status(
        self,
        status: object,
    ) -> None:
        with pytest.raises(ValueError):
            Reservation(
                id="RESERVATION#01",
                user_id="USER#01",
                ticket_tier_id="TICKET_TIER#01",
                quantity=1,
                status=status,  # ty:ignore[invalid-argument-type]
            )
