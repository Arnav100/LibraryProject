import inspect
from types import ModuleType
from inspect import getmembers, isfunction

from backend.adapters import orm
from backend.adapters.kafka import KafkaPublisher
from backend.service_layer import handlers, unit_of_work, messagebus, event_handlers


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = unit_of_work.UnitOfWork(),
    kafka_bootstrap_servers: str = 'localhost:9092'
) -> messagebus.MessageBus:

    if start_orm:
        orm.start_mappers()

    dependencies = {'uow': uow}
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    injected_event_handlers = {
        event_type: [inject_dependencies(handler, dependencies)]
        for event_type, handler in event_handlers.EVENT_HANDLERS.items()
    }

    kafka_publisher = KafkaPublisher(bootstrap_servers=kafka_bootstrap_servers)

    return messagebus.MessageBus(
        uow=uow,
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
        kafka_publisher=kafka_publisher
    )

def inject_dependencies(handler, dependencies: dict):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)