from abc import ABC, abstractmethod


class IOTPMessage(ABC):
    @property
    @abstractmethod
    def subject(self) -> str: ...

    @property
    @abstractmethod
    def body(self) -> str: ...
