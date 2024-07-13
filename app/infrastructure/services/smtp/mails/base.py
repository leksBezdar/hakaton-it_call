from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IMessage(ABC):
    @property
    @abstractmethod
    def subject(self) -> str: ...

    @property
    @abstractmethod
    def body(self) -> str: ...
