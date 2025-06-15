import abc
from typing import Set
from backend.adapters import orm
from backend.domain.models import Book, User
from sqlalchemy.orm.session import Session
from sqlalchemy import func

class AbstractBookRepository(abc.ABC):
    def __init__(self):
        self.seen: set[Book] = set()  

    def add(self, book: Book):
        self._add(book)
        self.seen.add(book)
        
    def get_all(self) -> list[Book]:
        return self._get_all()

    def get(self, id) -> Book:
        book = self._get(id)
        if book:
            self.seen.add(book)
        return book

    def search(self, name) -> list[Book]:
        books = self._search(name)
        return books

    @abc.abstractmethod
    def _add(self, book: Book):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id) -> Book:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> list[Book]:
        raise NotImplementedError
    
    @abc.abstractmethod
    def _search(self, name) -> list[Book]:
        raise NotImplementedError

class AbstractUserRepository(abc.ABC):
    def __init__(self):
        self.seen: set[User] = set()  

    def add(self, user: User):
        self._add(user)
        self.seen.add(user)
        
    def get_all(self) -> list[User]:
        return self._get_all()

    def get(self, id) -> User:
        user = self._get(id)
        if user:
            self.seen.add(user)
        return user

    def get_by_username(self, username: str) -> User:
        return self._get_by_username(username)

    @abc.abstractmethod
    def _add(self, user: User):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> list[User]:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_username(self, username: str) -> User:
        raise NotImplementedError

class BookRepository(AbstractBookRepository):

    def __init__(self, session: Session):
        super().__init__()
        self.session: Session = session

    def _add(self, book):
        self.session.add(book)

    def _get(self, id):
        return self.session.query(Book).filter_by(id=id).first()

    def _get_all(self):
        return self.session.query(Book).all()

    def _search(self, name) -> list[Book]:
        name = f"%{name}%"
        return self.session.query(Book).filter(Book.name.ilike(name)).all()

class UserRepository(AbstractUserRepository):
    
    def __init__(self, session: Session):
        super().__init__()
        self.session: Session = session

    def _add(self, user):
        self.session.add(user)

    def _get(self, id):
        return self.session.query(User).filter_by(id=id).first()

    def _get_all(self):
        return self.session.query(User).all()

    def _get_by_username(self, username: str) -> User:
        return self.session.query(User).filter_by(username=username).first()
      
        