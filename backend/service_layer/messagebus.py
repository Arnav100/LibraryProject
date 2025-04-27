# pylint: disable=broad-except, attribute-defined-outside-init
from __future__ import annotations
import logging
from typing import Callable, Dict, List, Union, Type, TYPE_CHECKING
from backend.domain import commands, events
from backend.adapters.kafka_publisher import KafkaPublisher

if TYPE_CHECKING:
    from . import unit_of_work

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        event_handlers: Dict[Type[events.Event], List[Callable]],
        command_handlers: Dict[Type[commands.Command], Callable],
        kafka_publisher: KafkaPublisher = None
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.kafka_publisher = kafka_publisher

    def handle(self, message: Message):
        if isinstance(message, events.Event):
            self.handle_event(message)
        elif isinstance(message, commands.Command):
            self.handle_command(message)
        else:
            raise Exception(f'{message} was not an Event or Command')
        self.publish_events()

    def handle_event(self, event: events.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                handler(event)
            except Exception:
                print('Exception handling event %s', event)
                continue

    def handle_command(self, command: commands.Command):
        print('handling command %s', command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
        except Exception:
            print('Exception handling command %s', command)
            raise
        
    def publish_events(self):
        for event in self.uow.collect_new_events():
            self.kafka_publisher.publish(event)