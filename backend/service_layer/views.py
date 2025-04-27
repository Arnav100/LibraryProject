import cattrs
from typing import List, Optional
from backend.domain.models import Book, User, Checkout
from .unit_of_work import AbstractUnitOfWork

class BookView:
    @staticmethod
    def get_all(uow: AbstractUnitOfWork) -> List[dict]:
        with uow:
            return [book.serialize() for book in uow.books.get_all()]
    
    @staticmethod
    def get_by_id(uow: AbstractUnitOfWork, book_id: int) -> Optional[dict]:
        with uow:
            book = uow.books.get(book_id)
            return book.serialize() if book else None
    
    @staticmethod
    def search(uow: AbstractUnitOfWork, query: str) -> List[dict]:
        with uow:
            return [book.serialize() for book in uow.books.search(query)]

class UserView:
    @staticmethod
    def get_all(uow: AbstractUnitOfWork) -> List[dict]:
        with uow:
            return [user.serialize() for user in uow.users.get_all()]
    
    @staticmethod
    def get_by_id(uow: AbstractUnitOfWork, user_id: int) -> Optional[dict]:
        with uow:
            user = uow.users.get(user_id)
            return user.serialize() if user else None

class CheckoutView:
    @staticmethod
    def get_all(uow: AbstractUnitOfWork) -> List[dict]:
        with uow:
            return [checkout.serialize() for checkout in uow.checkouts.get_all()] 
    
    @staticmethod
    def get_by_user(uow: AbstractUnitOfWork, user_id: int) -> List[dict]:
        with uow:
            return [checkout.serialize() for checkout in uow.checkouts.get_by_user(user_id)] 
        
class HoldView:
    @staticmethod
    def get_all(uow: AbstractUnitOfWork) -> List[dict]:
        with uow:
            return [hold.serialize() for hold in uow.holds.get_all()] 
    
    @staticmethod
    def get_by_user(uow: AbstractUnitOfWork, user_id: int) -> List[dict]:
        with uow:
            return [hold.serialize() for hold in uow.holds.get_by_user(user_id)] 
        