from pydantic import ValidationError
import pytest
from serverless_ticketing_notifications.ticketing.domain.event import Event


class TestId:
    def test_should_store_expected_value(self) -> None:
        event = Event(id="EVENT#01", name="TEST")

        assert event.id is not None
        assert type(event.id) is str
        assert event.id == "EVENT#01"

    @pytest.mark.parametrize(
        "event_id",
        [
            "EVENT#01       ",
            "       EVENT#01",
            "    EVENT#01   ",
        ],
    )
    def test_should_strip_id_surrounding_whitespace(self, event_id: str) -> None:
        event = Event(id=event_id, name="TEST")

        assert event.id is not None
        assert type(event.id) is str
        assert event.id == "EVENT#01"

    @pytest.mark.parametrize(
        "event_id",
        [
            True,
            10,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_id(self, event_id: object) -> None:
        with pytest.raises(ValidationError):
            Event(id=event_id, name="TEST")  # ty:ignore[invalid-argument-type]

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
            Event(id=event_id, name="EVENT#01")


class TestName:
    def test_should_store_expected_value(self) -> None:
        event = Event(id="EVENT#01", name="TEST")

        assert event.name is not None
        assert type(event.name) is str
        assert event.name == "TEST"

    @pytest.mark.parametrize(
        "name",
        [
            "TEST       ",
            "       TEST",
            "    TEST   ",
        ],
    )
    def test_should_strip_id_surrounding_whitespace(self, name: str) -> None:
        event = Event(id="EVENT#01", name=name)

        assert event.name is not None
        assert type(event.name) is str
        assert event.name == "TEST"

    @pytest.mark.parametrize(
        "name",
        [
            True,
            1,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_name(self, name: object) -> None:
        with pytest.raises(ValidationError):
            Event(name=name, id="EVENT#01")  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize(
        "name",
        [
            "",
            " ",
            "        ",
        ],
    )
    def test_should_reject_invalid_string_name(self, name: object) -> None:
        with pytest.raises(ValidationError):
            Event(name=name, id="EVENT#01")  # ty:ignore[invalid-argument-type]
