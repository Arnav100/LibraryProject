import cattrs
from datetime import datetime, timedelta
from backend.domain import commands

from .unit_of_work import AbstractUnitOfWork
from backend.domain.models import Book, User, Checkout, Hold



def add_book(cmd: commands.AddBook, uow: AbstractUnitOfWork):
    with uow: 
        book = Book(
            name=cmd.name,
            author=cmd.author,
            isbn=cmd.isbn,
            total_copies=cmd.total_copies,
            cover_url=cmd.cover_url,
            description=cmd.description
        )
        uow.books.add(book)
        uow.commit()
    

def add_user(cmd: commands.RegisterUser, uow: AbstractUnitOfWork):
    with uow:
        user = User(name=cmd.name, username=cmd.username, password=cmd.password)
        uow.users.add(user)
        uow.commit()


def checkout(cmd: commands.CheckoutBook, uow: AbstractUnitOfWork):
    with uow:
        book = uow.books.get(cmd.book_id)
        
        if not book:
            raise ValueError("Book not found")
        
        if book.available_copies < 1:
            raise ValueError("No available copies to checkout")
        
        user = uow.users.get(cmd.user_id)
        if not user:
            raise ValueError("User not found")
        
        checkout = Checkout.create(book, user, cmd.start_date, cmd.end_date)
        uow.checkouts.add(checkout)
        uow.commit()

def return_book(cmd: commands.ReturnBook, uow: AbstractUnitOfWork):
    with uow:
        checkout = uow.checkouts.get(cmd.checkout_id)
        if not checkout:
            raise ValueError("Checkout not found")
        
        checkout.return_book()
        uow.commit()
    
def place_hold(cmd: commands.PlaceHold, uow: AbstractUnitOfWork):
    with uow:
        book = uow.books.get(cmd.book_id)   
        
        if not book:
            raise ValueError("Book not found")
        
        user = uow.users.get(cmd.user_id)
        if not user:
            raise ValueError("User not found")
        
        next_position = uow.holds.get_next_position_on_book(cmd.book_id)
        new_hold = Hold(book_id=cmd.book_id, user_id=cmd.user_id, position=next_position)
        uow.holds.add(new_hold)
        uow.commit()

def remove_hold(cmd: commands.RemoveHold, uow: AbstractUnitOfWork):
    with uow: 
        hold = uow.holds.get(cmd.hold_id)
        if not hold: 
            raise ValueError("Hold does not exist")
        uow.holds.remove_hold(hold)
        uow.commit()
        
COMMAND_HANDLERS = {
    commands.AddBook: add_book,
    commands.CheckoutBook: checkout,
    commands.PlaceHold: place_hold,
    commands.RemoveHold: remove_hold,
    commands.RegisterUser: add_user,    
    commands.ReturnBook: return_book,
}   