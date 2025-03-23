from __future__ import annotations

import attr
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Book:
    name: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
    id: int | None = None
    created_at: datetime = datetime.now()
    
@dataclass
class User:
    name: str
    username: str
    password: str
    created_at: datetime = datetime.now()
    id: int | None = None


@dataclass
class Checkout:
    book: Book
    user: User
    start_date: datetime
    end_date: datetime
    returned: bool = False
    id: int | None = None

    
@dataclass
class Hold:
    book_id: int
    user_id: int
    position: int
    hold_date: datetime = datetime.now()
    id: int | None = None

