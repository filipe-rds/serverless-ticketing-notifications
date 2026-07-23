import pytest

from serverless_ticketing_notifications.ticketing.domain.entity.reservation import (
    Reservation,
    ReservationStatus,
)


@pytest.fixture
def pending_reservation():
    return Reservation(
        status=ReservationStatus.PENDING,
        id="RESERVATION#01",
        user_id="USER#01",
        ticket_tier_id="TICKET_TIER#01",
        quantity=1,
    )


class TestBehavior:
    def test_should_confirm_pending_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.confirm()

        assert pending_reservation.status == ReservationStatus.CONFIRMED

    def test_should_cancel_pending_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.cancel()

        assert pending_reservation.status == ReservationStatus.CANCELLED

    def test_should_expire_pending_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.expire()

        assert pending_reservation.status == ReservationStatus.EXPIRED

    def test_should_not_confirm_cancelled_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.cancel()

        with pytest.raises(ValueError):
            pending_reservation.confirm()

    def test_should_not_cancel_expired_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.expire()

        with pytest.raises(ValueError):
            pending_reservation.cancel()

    def test_should_not_cancel_confirmed_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.confirm()

        with pytest.raises(ValueError):
            pending_reservation.cancel()

    def test_should_not_confirm_expired_reservation(
        self, pending_reservation: Reservation
    ) -> None:
        pending_reservation.expire()

        with pytest.raises(ValueError):
            pending_reservation.confirm()
