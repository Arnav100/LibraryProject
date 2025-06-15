from attr import define
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@define
class Command:
    pass

@define(frozen=True)
class AddBook(Command):
    name: str
    author: str
    isbn: str
    total_copies: int
    cover_url: str | None = None
    description: str | None = None

@define(frozen=True)
class RemoveBook(Command):
    book_id: int


@define(frozen=True)
class RegisterUser(Command):
    name: str
    username: str
    password: str


@dataclass
class RequestBook(Command):
    book_title: str
    author: str
    requester_id: int
    notes: Optional[str] = None

@dataclass
class UpdateRequestStatus(Command):
    request_id: int
    new_status: str

@dataclass
class GetFriendSpending(Command):
    friend_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@dataclass
class GetFriendGifts(Command):
    friend_id: int
    include_delivered: bool = True
    include_pending: bool = True
