from abc import ABC, abstractmethod
from typing import TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class UseCase[InputT, OutputT](ABC):
    @abstractmethod
    def execute(self, input: InputT) -> OutputT: ...
