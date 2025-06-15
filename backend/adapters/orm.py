from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey, Boolean, event, Numeric, DateTime
)
from sqlalchemy.orm import registry, relationship

from backend.domain.models import User, Book, BookGift, BookRequest

metadata = MetaData()

books = Table(
    'books', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('author', String(255), nullable=False),
    Column('isbn', String(255), nullable=False),
    Column('price', Numeric(10, 2), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('cover_url', String(255)),
    Column('description', String(255)),
)

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('username', String(255), nullable=False, unique=True),
    Column('password', String(255), nullable=False),
    Column('email', String(255), nullable=False),
    Column('created_at', DateTime, nullable=False),
)

book_gifts = Table(
    'gifts', metadata,
    Column('id', Integer, primary_key=True),
    Column('book_id', ForeignKey('books.id'), nullable=False),
    Column('giver_id', ForeignKey('users.id'), nullable=False),
    Column('recipient_id', ForeignKey('users.id'), nullable=False),
    Column('note', String(255)),
    Column('approved', Boolean, nullable=False, default=False),
    Column('created_at', DateTime, nullable=False),
)

book_requests = Table(
    'wishlist', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('users.id'), nullable=False),
    Column('title', String(255), nullable=False),
    Column('shop_url', String(255), nullable=False),
    Column('price_cents', Integer, nullable=False),
    Column('note', String(255)),
    Column('fulfilled', Boolean, nullable=False, default=False),
    Column('requested_at', DateTime, nullable=False),
)

def start_mappers():
    mapper_registry = registry()

    users_mapper = mapper_registry.map_imperatively(User, users)
    books_mapper = mapper_registry.map_imperatively(Book, books)
    book_gifts_mapper = mapper_registry.map_imperatively(BookGift, book_gifts, properties={
        'book': relationship(Book),
        'giver': relationship(User, foreign_keys=[book_gifts.c.giver_id]),
        'recipient': relationship(User, foreign_keys=[book_gifts.c.recipient_id])
    })

    book_requests_mapper = mapper_registry.map_imperatively(BookRequest, book_requests, properties={
        'user': relationship(User),
        'price': book_requests.c.price_cents
    })

@event.listens_for(Book, 'load')
def receive_load(book, _):
    book.events = []

@event.listens_for(User, 'load')
def receive_load(user, _):
    user.events = []

@event.listens_for(BookGift, 'load')
def receive_load(book_gift, _):
    book_gift.events = []

@event.listens_for(BookRequest, 'load')
def receive_load(book_request, _):
    book_request.events = []