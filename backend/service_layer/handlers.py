import cattrs
from datetime import datetime, timedelta
from backend.domain import commands

from .unit_of_work import AbstractUnitOfWork
from backend.domain.models import Book, User, BookRequest



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


def request_book(cmd: commands.RequestBook, uow: AbstractUnitOfWork):
    with uow:
        user = uow.users.get(cmd.requester_id)
        if not user:
            raise ValueError(f"User with id {cmd.requester_id} not found")
        
        book_request = BookRequest(
            title=cmd.title,
            shop_url=cmd.shop_url,
            price=cmd.price,
            user=user,
            note=cmd.note
        )
        uow.book_requests.add(book_request)
        uow.commit()
        
COMMAND_HANDLERS = {
    commands.AddBook: add_book,
    commands.RegisterUser: add_user,       
    commands.RequestBook: request_book,
}   