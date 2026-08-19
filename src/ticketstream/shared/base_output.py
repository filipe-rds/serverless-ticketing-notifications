from dataclasses import asdict, dataclass


@dataclass
class BaseOutput:
    def to_dict(self) -> dict:
        return asdict(self)
