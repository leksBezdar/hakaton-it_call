from dataclasses import dataclass

from domain.events.users import (
    UserCreatedEvent,
    UserDeletedEvent,
)
from infrastructure.message_brokers.converters import convert_event_to_broker_message
from logic.events.base import EventHandler


@dataclass
class NewUserCreatedEventHandler(EventHandler[UserCreatedEvent, None]):
    async def handle(self, event: UserCreatedEvent) -> None:
        await self.message_broker.send_message(
            topic=self.broker_topic,
            value=convert_event_to_broker_message(event=event),
            key=event.event_id.encode(),
        )


@dataclass
class UserDeletedEventHandler(EventHandler[UserDeletedEvent, None]):
    async def handle(self, event: UserDeletedEvent) -> None:
        await self.message_broker.send_message(
            topic=self.broker_topic,
            value=convert_event_to_broker_message(event=event),
            key=event.event_id.encode(),
        )
