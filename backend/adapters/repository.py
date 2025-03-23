import abc
from typing import Set
from backend.adapters import orm
from backend.domain.models import Book, User, Checkout, Hold
from sqlalchemy.orm.session import Session
from sqlalchemy import func



class AbstractBookRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  

    def add(self, book: Book):
        self._add(book)
        # self.seen.add(book)
        
    def get_all(self) -> list[Book]:
        return self._get_all()

    def get(self, id) -> Book:
        book = self._get(id)
        # if book:
        #     self.seen.add(book)
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
        self.seen = set()  

    def add(self, user: User):
        self._add(user)
        # self.seen.add(book)
        
    def get_all(self) -> list[User]:
        return self._get_all()

    def get(self, id) -> User:
        user = self._get(id)
        # if user:
        #     self.seen.add(user)
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

class AbstractCheckoutRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  

    def add(self, checkout: Checkout):
        self._add(checkout)
        # self.seen.add(book)
        
    def get_all(self) -> list[Checkout]:
        return self._get_all()

    def get(self, id) -> Checkout:
        checkout = self._get(id)
        if checkout:
            self.seen.add(checkout)
        return checkout

    @abc.abstractmethod
    def _add(self, checkout: Checkout):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id) -> Checkout:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> list[Checkout]:
        raise NotImplementedError

class AbstractHoldRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  

    def add(self, hold: Hold):
        self._add(hold)
        # self.seen.add(book)
        
    def get_all(self) -> list[Hold]:
        return self._get_all()

    def get(self, id) -> Hold:
        hold = self._get(id)
        # if hold:
        #     self.seen.add(hold)
        return hold
    
    def get_next_position_on_book(self, book_id):
        raise NotImplementedError
    
    def remove_hold(self, hold: Hold):
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, checkout: Hold):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id) -> Hold:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> list[Hold]:
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
    
class CheckoutRepository(AbstractCheckoutRepository):
    
    def __init__(self, session: Session):
        super().__init__()
        self.session: Session = session
        
    def _add(self, checkout):
        self.session.add(checkout)
        
    def _get(self, id):
        return self.session.query(Checkout).filter_by(id=id).first()
    
    def _get_all(self):
        return self.session.query(Checkout).all()

class HoldRepository(AbstractHoldRepository):
    def __init__(self, session: Session):
        super().__init__()
        self.session: Session = session
        
    def _add(self, hold):
        self.session.add(hold)
        
    def _get(self, id):
        return self.session.query(Hold).filter_by(id=id).first()
    
    def _get_all(self):
        return self.session.query(Hold).all()
    
    def get_next_position_on_book(self, book_id):
        return self.session.query(func.coalesce(func.max(Hold.position), 0) + 1).filter(Hold.book_id == book_id).scalar()
    
    def remove_hold(self, hold: Hold):
        self.session.delete(hold)
        self.session.query(Hold).filter(Hold.book_id == hold.book_id, Hold.position > hold.position) \
            .update({"position": Hold.position - 1}, synchronize_session=False)