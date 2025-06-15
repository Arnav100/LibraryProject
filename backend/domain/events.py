from attr import define
import json
import cattrs
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@define
class Event:
    
    def serialize(self) -> str:
        return json.dumps({
        "event_type": self.__class__.__name__,
        "payload": cattrs.unstructure(self),
    }, default=str)
        
@define(frozen=True)
class Notification(Event):
    user_id: int
    type: str
    message: str

@define(frozen=True)
class BookReturned(Event):
    book_id: int
    user_id: int

@define(frozen=True)
class BookCheckedOut(Event):
    book_id: int
    user_id: int
    start_date: str
    end_date: str

@define(frozen=True)
class BookPlacedOnHold(Event):
    book_id: int
    user_id: int
    hold_date: str

@define(frozen=True)
class BookAdded(Event):
    pass

@define(frozen=True)
class BookRemoved(Event):
    pass

@define(frozen=True)
class HoldUpdated(Event):
    book_id: int
    user_id: int
    old_position: int
    new_position: int

@dataclass
class GiftStatusUpdated(Event):
    gift_id: int
    new_status: str

@dataclass
class RequestStatusUpdated(Event):
    request_id: int
    new_status: str

@dataclass
class FriendAdded(Event):
    friend_id: int
    added_by_id: int

@dataclass
class BookGifted(Event):
    book_id: int
    giver_id: int
    recipient_id: int
    gift_date: datetime

@dataclass
class BookRequested(Event):
    request_id: int
    requester_id: int
    book_title: str
    author: str
    request_date: datetime
    
    