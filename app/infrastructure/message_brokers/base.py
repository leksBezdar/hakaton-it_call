from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IMessageBroker(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def send_message(self, key: str, topic: str, value: bytes): ...

    @abstractmethod
    async def start_consuming(self, topic: str): ...

    @abstractmethod
    async def stop_consuming(self, topic: str): ...
