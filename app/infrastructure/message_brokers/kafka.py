from dataclasses import dataclass
from typing import AsyncIterator

import orjson

from infrastructure.message_brokers.base import IMessageBroker
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


@dataclass
class KafkaMessageBroker(IMessageBroker):
    producer: AIOKafkaProducer
    consumer: AIOKafkaConsumer

    async def send_message(self, key: bytes, topic: str, value: bytes):
        await self.producer.send(topic=topic, key=key, value=value)

    async def start_consuming(self, topic: str) -> AsyncIterator[dict]:
        self.consumer.subscribe(topics=[topic])

        async for message in self.consumer:
            yield orjson.loads(message.value)

    async def stop_consuming(self):
        self.consumer.unsubscribe()

    async def stop(self):
        await self.consumer.stop()
        await self.producer.stop()

    async def start(self):
        await self.consumer.start()
        await self.producer.start()
