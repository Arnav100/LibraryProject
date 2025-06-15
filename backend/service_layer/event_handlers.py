from typing import Dict, Type, Callable
from backend.domain import events
from backend.service_layer.unit_of_work import AbstractUnitOfWork
import logging
import json
import redis


EVENT_HANDLERS: Dict[Type[events.Event], Callable] = {
 
} 