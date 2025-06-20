from __future__ import annotations

import attr
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from backend.domain import events

class Model:
    def serialize(self) -> dict:
        def serialize_value(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, Model):
                return value.serialize()
            elif isinstance(value, Decimal):
                return str(value)
            return value

        return {
            key: serialize_value(value)
            for key, value in self.values().items()
            if not key.startswith("_") and not key.startswith("events")
        }
    
    def values(self) -> dict:
        return self.__dict__

class User(Model):
    def __init__(self, name: str, username: str, password: str, email: str):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.created_at = datetime.now()
        self.id = None
        self.events = []
        
    def send_notification(self, type: str, message: str):
        self.events.append(events.Notification(self.id, type, message))

class Book(Model):
    def __init__(self, name: str, author: str, isbn: str, price: Decimal, 
                 cover_url: Optional[str] = None, description: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.name = name
        self.author = author
        self.isbn = isbn
        self.price = price
        self.cover_url = cover_url
        self.description = description
        self.created_at = created_at if created_at else datetime.now()
        self.id = None
        self.events = []

class BookGift(Model):
    def __init__(self, book: Book, recipient: User, 
                 giver: User, note: Optional[str] = None, 
                 approved: bool = False, created_at: Optional[datetime] = None):
        self.book = book
        self.giver = giver
        self.recipient = recipient
        self.note = note    
        self.approved = approved
        self.created_at = created_at if created_at else datetime.now()
        self.id = None
        self.events = []
        
    def update_approval(self, new_status: bool):
        self.approved = new_status
        self.events.append(events.GiftStatusUpdated(self.id, new_status))
        
    def values(self) -> dict:
        return {
            "book": self.book,
            "giver": self.giver,
            "recipient": self.recipient,
            "gift_date": self.gift_date,
            "delivery_status": self.delivery_status,
            "id": self.id
        }

class BookRequest(Model):
    def __init__(self, user: User, title: str, 
                 shop_url: str, price: int, 
                 note: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 fulfilled: bool = False):
        self.user = user
        self.title = title
        self.shop_url = shop_url
        self.price_cents = price
        self.note = note
        self.fulfilled = fulfilled
        self.created_at = created_at if created_at else datetime.now()
        self.id = None
        self.events = []
        

    def values(self) -> dict:
        return {
            "book_title": self.book_title,
            "author": self.author,
            "requester": self.requester,
            "request_date": self.request_date,
            "status": self.status,
            "notes": self.notes,
            "id": self.id
        }

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
