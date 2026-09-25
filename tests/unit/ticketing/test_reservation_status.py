import pytest

from ticketstream.ticketing.domain.enumerators.reservation_status import (
    ReservationStatus,
)

TERMINAL_STATUSES = {
    ReservationStatus.CONFIRMED,
    ReservationStatus.CANCELLED,
    ReservationStatus.EXPIRED,
}


@pytest.mark.parametrize("target", list(ReservationStatus))
@pytest.mark.parametrize("current", list(ReservationStatus))
def test_only_pending_transitions_and_only_to_a_terminal_status(
    current: ReservationStatus, target: ReservationStatus
) -> None:
    # A regra inteira em uma assercao: PENDING e o unico estado nao terminal, e dele
    # saem exatamente as tres transicoes para CONFIRMED, CANCELLED e EXPIRED.
    # Cobre a matriz 4x4, incluindo CONFIRMED -> CANCELLED (secao 10 do AGENTS.md).
    expected = current is ReservationStatus.PENDING and target in TERMINAL_STATUSES

    assert current.can_transition_to(target) is expected
