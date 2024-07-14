from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class IScheduler(ABC):
    @abstractmethod
    async def send_reminder() -> None: ...

    @abstractmethod
    async def start() -> None: ...

    @abstractmethod
    async def stop() -> None: ...
