from dataclasses import dataclass, asdict


@dataclass
class BaseOutput:
    def to_dict(self) -> dict:
        return asdict(self)
