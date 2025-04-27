from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey, Boolean, event
)
from sqlalchemy.orm import registry, relationship

from backend.domain.models import User, Book, Checkout, Hold

metadata = MetaData()

books = Table(
    'books', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('author', String(255), nullable=False),
    Column('isbn', String(255), nullable=False),
    Column('total_copies', Integer, nullable=False),
    Column('available_copies', Integer, nullable=False),
    Column('created_at', Date, nullable=False),
    Column('cover_url', String(255)),
    Column('description', String(255)),
)

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('username', String(255), nullable=False, unique=True),
    Column('password', String(255), nullable=False),
    Column('created_at', Date, nullable=False),
)

checkouts = Table(
    'checkouts', metadata,
    Column('id', Integer, primary_key=True),
    Column('book_id', ForeignKey('books.id')),
    Column('user_id', ForeignKey('users.id')),
    Column('start_date', Date),
    Column('end_date', Date),
    Column('returned', Boolean),
)

holds = Table(
    'holds', metadata,
    Column('id', Integer, primary_key=True),
    Column('book_id', ForeignKey('books.id')),
    Column('user_id', ForeignKey('users.id')),
    Column('position', Integer),
    Column('hold_date', Date),
)

def start_mappers():
    mapper_registry = registry()

    users_mapper = mapper_registry.map_imperatively(User, users)
    books_mapper = mapper_registry.map_imperatively(Book, books)
    checkouts_mapper = mapper_registry.map_imperatively(Checkout, checkouts, properties={
        'book': relationship(Book),
        'user': relationship(User)
    })
    
    holds_mapper = mapper_registry.map_imperatively(Hold, holds, properties={
        'book': relationship(Book),
        'user': relationship(User)
    })

@event.listens_for(Book, 'load')
def receive_load(book, _):
    book.events = []

@event.listens_for(User, 'load')
def receive_load(user, _):
    user.events = []

@event.listens_for(Checkout, 'load')
def receive_load(checkout, _):
    checkout.events = []

@event.listens_for(Hold, 'load')
def receive_load(hold, _):
    hold.events = []