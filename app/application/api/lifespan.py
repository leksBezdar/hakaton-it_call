from infrastructure.message_brokers.base import IMessageBroker
from logic.init import init_container


async def init_message_broker():
    container = init_container()
    message_broker: IMessageBroker = container.resolve(IMessageBroker)
    await message_broker.start()


async def close_message_broker():
    container = init_container()
    message_broker: IMessageBroker = container.resolve(IMessageBroker)
    await message_broker.stop()
