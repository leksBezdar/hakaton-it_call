from infrastructure.message_brokers.base import IMessageBroker
from infrastructure.scheduler.base import IScheduler
from logic.init import init_container


async def init_message_broker():
    container = init_container()
    message_broker: IMessageBroker = container.resolve(IMessageBroker)
    await message_broker.start()


async def close_message_broker():
    container = init_container()
    message_broker: IMessageBroker = container.resolve(IMessageBroker)
    await message_broker.stop()


async def init_scheduler():
    container = init_container()
    email_scheduler: IScheduler = container.resolve(IScheduler)
    await email_scheduler.start()


async def close_scheduler():
    container = init_container()
    email_scheduler: IScheduler = container.resolve(IScheduler)
    await email_scheduler.stop()
