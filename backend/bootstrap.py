import inspect
from types import ModuleType
from inspect import getmembers, isfunction

from backend.adapters import orm

from backend.service_layer import handlers, unit_of_work


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = unit_of_work.UnitOfWork(),
) -> ModuleType:

    if start_orm:
        orm.start_mappers()

    dependencies = {'uow': uow}
    for method_name, handler in getmembers(handlers, isfunction):
        setattr(handlers, method_name, inject_dependencies(handler, dependencies))
    
    return handlers


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda *args, **kwargs: handler(*args, **kwargs, **deps)