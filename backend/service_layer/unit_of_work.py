from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from backend.domain.models import Model
from backend.domain.events import Event
from typing import Generator

from backend import config
from backend.adapters import repository

class AbstractUnitOfWork(abc.ABC):
    books: repository.AbstractBookRepository
    users: repository.AbstractUserRepository
    book_gifts: repository.AbstractBookGiftRepository
    book_requests: repository.AbstractBookRequestRepository
    
    
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self) -> Generator[Event, None, None]:
        for repo in self._repositories():
            for model in repo.seen:
                while model.events:
                    yield model.events.pop(0)       

    def _repositories(self) -> list[repository.AbstractRepository[Model]]:
        # Extend this list as you add repositories
        return [self.books, self.users, self.book_gifts, self.book_requests]

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError



DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_mysql_url(),
    isolation_level="REPEATABLE READ",
))

class UnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()  
        self.books = repository.BookRepository(self.session)
        self.users = repository.UserRepository(self.session)
        self.book_gifts = repository.BookGiftRepository(self.session)
        self.book_requests = repository.BookRequestRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()