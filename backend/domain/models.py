from __future__ import annotations

import attr
from datetime import datetime, timedelta
from dataclasses import dataclass
from backend.domain import events

class Model:
    def serialize(self) -> dict:
        def serialize_value(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, Model):
                return value.serialize()
            return value

        return {
            key: serialize_value(value)
            for key, value in self.values().items()
            if not key.startswith("_") and not key.startswith("events")
        }
    
    def values(self) -> dict:
        return self.__dict__

class Book(Model):
    
    def __init__(self, name: str, author: str, isbn: str, total_copies: int, cover_url: str | None = None, description: str | None = None):
        self.name = name
        self.author = author
        self.isbn = isbn
        self.total_copies = total_copies
        self.available_copies = total_copies
        self.id = None
        self.cover_url = cover_url
        self.description = description
        self.created_at = datetime.now()
        print(f"BOOK INIT: {self.name}")
        self.events = []
    
    def book_returned(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.events.append(events.BookReturned(self.id))

class User(Model):
    
    def __init__(self, name: str, username: str, password: str):
        self.name = name
        self.username = username
        self.password = password
        self.created_at = datetime.now()
        self.id = None
        self.events = []

class Checkout(Model):
    
    def __init__(self, book: Book, user: User, start_date: datetime | None = None, end_date: datetime | None = None):
        self.book = book
        self.user = user
        self.start_date = start_date if start_date else datetime.now()
        self.end_date = end_date if end_date else self.start_date + timedelta(days=15)
        self.returned = False
        self.id = None
        self.events = []
        
    def values(self) -> dict:
        return {
            "book": self.book,
            "user": self.user,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "returned": self.returned,
            "id": self.id
        }
    
    @classmethod
    def create(cls, book: Book, user: User, start_date: datetime | None, end_date: datetime | None):
        checkout = cls(book, user, start_date, end_date)
        book.available_copies -= 1
        checkout.events.append(events.BookCheckedOut(book.id, user.id, checkout.start_date, checkout.end_date))
        return checkout
    

    def return_book(self):
        self.book.available_copies += 1
        self.returned = True
        self.events.append(events.BookReturned(self.book.id, self.user.id))

    
class Hold(Model):
    
    def __init__(self, book: Book, user: User, position: int):
        self.book = book
        self.user = user
        self.position = position
        self.hold_date = datetime.now()
        self.id = None
        self.events = []
    
    def move_up(self):
        print(f"Moving hold up for book {self.book_id} by user {self.user_id}. Current position: {self.position}")
        self.position -= 1
        self.events.append(
            events.HoldUpdated(
                book_id=self.book_id,
                user_id=self.user_id,
                old_position=self.position + 1,
                new_position=self.position
            )
        )
        
    def values(self) -> dict:
        return {
            "book": self.book,
            "user": self.user,
            "position": self.position,
            "hold_date": self.hold_date,
            "id": self.id
        }
