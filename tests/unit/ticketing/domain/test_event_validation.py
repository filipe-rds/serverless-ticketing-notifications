from pydantic import ValidationError
import pytest

from serverless_ticketing_notifications.ticketing.domain.entity.event import Event

def make_event(**overrides: object) -> Event:
    data: dict[str, object] = {
        "id": "EVENT#01",
        "name": "vnt.school",
        "description": "Description of vnt.school",
    }
    data.update(overrides)

    return Event(**data)

class TestId:
    def test_should_store_expected_value(self) -> None:
        event = make_event(id="EVENT#01")

        assert event.id is not None
        assert type(event.id) is str
        assert event.id == "EVENT#01"

    @pytest.mark.parametrize(
        "id",
        [
            "EVENT#01       ",
            "       EVENT#01",
            "    EVENT#01   ",
        ],
    )
    def test_should_strip_id_surrounding_whitespace(self, id: str) -> None:
        event = make_event(id=id)

        assert event.id is not None
        assert type(event.id) is str
        assert event.id == "EVENT#01"

    @pytest.mark.parametrize("id", [True, 10, 1.0])
    def test_should_reject_non_string_id(self, id: object) -> None:
        with pytest.raises(ValidationError):
            make_event(id=id)

    @pytest.mark.parametrize(
        "id",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_id(self, id: str) -> None:
        with pytest.raises(ValidationError):
            make_event(id=id)


class TestName:
    def test_should_store_expected_value(self) -> None:
        event = make_event(name="vnt.school")

        assert event.name is not None
        assert type(event.name) is str
        assert event.name == "vnt.school"

    @pytest.mark.parametrize(
        "name",
        [
            "vnt.school       ",
            "       vnt.school",
            "    vnt.school   ",
        ],
    )
    def test_should_strip_name_surrounding_whitespace(self, name: str) -> None:
        event = make_event(name=name)

        assert event.name is not None
        assert type(event.name) is str
        assert event.name == "vnt.school"

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
            make_event(name=name)

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
            make_event(name=name)
            
class TestDescription:
    def test_should_store_expected_value(self) -> None:
        event = make_event(description="Description of vnt.school")

        assert event.description is not None
        assert type(event.description) is str
        assert event.description == "Description of vnt.school"

    @pytest.mark.parametrize(
        "description",
        [
            "Description of vnt.school       ",
            "       Description of vnt.school",
            "    Description of vnt.school   ",
        ],
    )
    def test_should_strip_description_surrounding_whitespace(self, description: str) -> None:
        event = make_event(description=description)

        assert event.description is not None
        assert type(event.description) is str
        assert event.description == "Description of vnt.school"

    @pytest.mark.parametrize(
        "description",
        [
            10,
            1.0,
            object(),
        ],
    )
    def test_should_reject_non_string_description(self, description: object) -> None:
        with pytest.raises(ValidationError):
            make_event(description=description)

    @pytest.mark.parametrize(
        "description",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_reject_invalid_string_description(self, description: str) -> None:
        with pytest.raises(ValidationError):
            make_event(description=description)
