
from attr import define
import json
import cattrs

@define
class Event:
    
    def serialize(self) -> str:
        return json.dumps({
        "event_type": self.__class__.__name__,
        "payload": cattrs.unstructure(self),
    }, default=str)

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
    
    