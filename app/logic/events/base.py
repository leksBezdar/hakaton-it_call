from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from domain.events.base import BaseEvent
from infrastructure.message_brokers.base import IMessageBroker


ET = TypeVar("ET", bound=BaseEvent)
ER = TypeVar("ER", bound=Any)


@dataclass
class EventHandler(ABC, Generic[ET, ER]):
    message_broker: IMessageBroker
    broker_topic: str | None = None

    def handle(self, event: ET) -> ER: ...
