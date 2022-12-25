from abc import ABC, abstractmethod


class Notifier(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def notify(self, title: str, message: str, url: str = "") -> None:
        pass
