from typing import Protocol


class UseCase[Input, Output](Protocol):
    def execute(self, request: Input) -> Output: ...
