import abc
from typing import Type, TypeVar
from typing import Generic
from backend.domain.models import Model, Book, User, BookGift, BookRequest  
from sqlalchemy.orm.session import Session

T = TypeVar('T', bound=Model)   

class AbstractRepository(abc.ABC, Generic[T]):
    seen: set[T] = set()
    
    def add(self, model: T):
        self._add(model)
        self.seen.add(model)
        
    def get_all(self) -> list[T]:
        return self._get_all()
        
    def get(self, id: int) -> T:
        model = self._get(id)
        if model:
            self.seen.add(model)
        return model
    
    @abc.abstractmethod
    def _add(self, model: T):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id: int) -> T:
        raise NotImplementedError
    
    @abc.abstractmethod
    def _get_all(self) -> list[T]:
        raise NotImplementedError

class SQLAlchemyRepository(AbstractRepository[T]):
    def __init__(self, session: Session, model_cls: Type[T]):
        super().__init__()
        self.session = session
        self.model_cls = model_cls
        
    def _add(self, model: T):
        self.session.add(model)
        
    def _get(self, id: int) -> T:
        return self.session.query(self.model_cls).filter_by(id=id).first()
    
    def _get_all(self) -> list[T]:
        return self.session.query(self.model_cls).all()
        
class AbstractBookRepository(AbstractRepository[Book]):

    def search(self, name: str) -> list[Book]:
        return self._search(name)

    @abc.abstractmethod
    def _search(self, name: str) -> list[Book]:
        raise NotImplementedError

class AbstractUserRepository(AbstractRepository[User]):

    def get_by_username(self, username: str) -> User:
        return self._get_by_username(username)

    @abc.abstractmethod
    def _get_by_username(self, username: str) -> User:
        raise NotImplementedError

class AbstractBookGiftRepository(AbstractRepository[BookGift]):

    def get_all_by_user(self, user_id: int) -> list[BookGift]:
        return self._get_all_by_user(user_id)

    @abc.abstractmethod
    def _get_all_by_user(self, user_id: int) -> list[BookGift]:
        raise NotImplementedError

class AbstractBookRequestRepository(AbstractRepository[BookRequest]):

    def get_all_by_user(self, user_id: int) -> list[BookRequest]:
        return self._get_all_by_user(user_id)

    @abc.abstractmethod
    def _get_all_by_user(self, user_id: int) -> list[BookRequest]:
        raise NotImplementedError

class BookRepository(SQLAlchemyRepository[Book], AbstractBookRepository):

    def __init__(self, session: Session):
        super().__init__(session, Book)

    def _search(self, name) -> list[Book]:
        name = f"%{name}%"
        return self.session.query(Book).filter(Book.name.ilike(name)).all()

class UserRepository(SQLAlchemyRepository[User], AbstractUserRepository):
    
    def __init__(self, session: Session):
        super().__init__(session, User)

    def _get_by_username(self, username: str) -> User:
        return self.session.query(User).filter_by(username=username).first()
      
class BookGiftRepository(SQLAlchemyRepository[BookGift], AbstractBookGiftRepository):

    def __init__(self, session: Session):
        super().__init__(session, BookGift)

    def _get_all_by_user(self, user_id: int) -> list[BookGift]:
        return self.session.query(BookGift).filter_by(user_id=user_id).all()

class BookRequestRepository(SQLAlchemyRepository[BookRequest], AbstractBookRequestRepository):

    def __init__(self, session: Session):
        super().__init__(session, BookRequest)

    def _get_all_by_user(self, user_id: int) -> list[BookRequest]:
        return self.session.query(BookRequest).filter_by(user_id=user_id).all()