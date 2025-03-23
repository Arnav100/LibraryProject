import cattrs
from datetime import datetime, timedelta


from .unit_of_work import AbstractUnitOfWork
from backend.domain.models import Book, User, Checkout, Hold


def get_books(uow: AbstractUnitOfWork):
    with uow:
        return cattrs.unstructure(uow.books.get_all())
    
def add_book(uow: AbstractUnitOfWork, book: dict):
    with uow: 
        book = cattrs.structure(book, Book)
        uow.books.add(book)
        uow.commit()
        return cattrs.unstructure(book)
    
def get_book(uow: AbstractUnitOfWork, book_id: int):
    with uow:
        book = uow.books.get(book_id)
        return cattrs.unstructure(book)
    
def get_users(uow: AbstractUnitOfWork):
    with uow:
        return cattrs.unstructure(uow.users.get_all())

def add_user(uow: AbstractUnitOfWork, user: dict):
    with uow:
        user = cattrs.structure(user, User)
        uow.users.add(user)
        uow.commit()
        return cattrs.unstructure(user)

def get_checkouts(uow: AbstractUnitOfWork):
    with uow:
        return cattrs.unstructure(uow.checkouts.get_all())

def checkout(uow: AbstractUnitOfWork, user_id, book_id):
    with uow:
        book = uow.books.get(book_id)
        
        if not book:
            raise ValueError("Book not found")
        
        if book.available_copies < 1:
            raise ValueError("No available copies to checkout")
        
        user = uow.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        due_date = datetime.now() + timedelta(days=15)
        checkout = Checkout(
            user=user,  
            book=book, 
            start_date=datetime.now(),
            end_date=due_date,
            returned=False
        )
        uow.checkouts.add(checkout)
        book.available_copies -= 1
        uow.commit()
        return cattrs.unstructure(checkout)

def search_book(uow: AbstractUnitOfWork, name):
    with uow:
        return cattrs.unstructure(uow.books.search(name))
    
def place_hold(uow: AbstractUnitOfWork, user_id: int, book_id: int):
    with uow:
        book = uow.books.get(book_id)
        
        if not book:
            raise ValueError("Book not found")
        
        user = uow.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        next_position = uow.holds.get_next_position_on_book(book_id)
        new_hold = Hold(book_id=book_id, user_id=user_id, position=next_position)
        uow.holds.add(new_hold)
        uow.commit()
        return cattrs.unstructure(new_hold)

def remove_hold(uow: AbstractUnitOfWork, hold_id: int):
    with uow: 
        hold = uow.holds.get(hold_id)
        if not hold: 
            raise ValueError("Hold does not exist")
        uow.holds.remove_hold(hold)
        uow.commit()