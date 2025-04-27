from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


from backend import config
from backend.adapters import repository

class AbstractUnitOfWork(abc.ABC):
    books: repository.AbstractBookRepository
    users: repository.AbstractUserRepository
    checkouts: repository.AbstractCheckoutRepository
    holds: repository.AbstractHoldRepository
    
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for book in self.books.seen:
            while book.events:
                yield book.events.pop(0)
        
        for user in self.users.seen:
            while user.events:
                yield user.events.pop(0)

        for checkout in self.checkouts.seen:
            while checkout.events:
                yield checkout.events.pop(0)
                
        for hold in self.holds.seen:
            while hold.events:
                yield hold.events.pop(0)    

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
        self.checkouts = repository.CheckoutRepository(self.session)
        self.holds = repository.HoldRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()