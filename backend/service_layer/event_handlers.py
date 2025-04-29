from typing import Dict, Type, Callable
from backend.domain import events
from backend.service_layer.unit_of_work import AbstractUnitOfWork
import logging
import json
import redis


def handle_book_checked_out(event: events.BookCheckedOut, uow: AbstractUnitOfWork):
    with uow:
        checkout = uow.checkouts.get_by_info(event.book_id, event.user_id)
        print(f"Book {checkout.book.name} was checked out by user {checkout.user.name}")
        # Send notification to user
        
def handle_book_returned(event: events.BookReturned, uow: AbstractUnitOfWork):
    with uow:
        holds = uow.holds.get_by_book_id(event.book_id)
        for hold in holds:
            hold.move_up()
        # Send notification to user
        uow.commit()

def handle_hold_updated(event: events.HoldUpdated, uow: AbstractUnitOfWork):
    with uow:
        user = uow.users.get(event.user_id)
        book = uow.books.get(event.book_id)
        print(f"Hold updated for book {book.name} by user {user.name}")
        
        # Publish notification to Redis
        redis_client = redis.Redis(host='localhost', port=6380, db=0)
        notification = {
            "type": "hold_updated",
            "message": f"Your hold position for '{book.name}' has changed to {event.new_position}",
            "book_id": event.book_id,
            "new_position": event.new_position,
            "user_id": event.user_id
        }
        redis_client.publish('notifications', json.dumps(notification))
        
        uow.commit()

# def handle_hold_placed(event: events.HoldPlaced, uow: AbstractUnitOfWork):
#     with uow:
#         logger.info(f"Hold placed on book {event.book_id} by user {event.user_id}")
#         # Add any additional processing here
#         uow.commit()

# def handle_hold_removed(event: events.HoldRemoved, uow: AbstractUnitOfWork):
#     with uow:
#         logger.info(f"Hold removed from book {event.book_id} by user {event.user_id}")
#         # Add any additional processing here
#         uow.commit()

EVENT_HANDLERS: Dict[Type[events.Event], Callable] = {
    events.BookCheckedOut: handle_book_checked_out,
    events.BookReturned: handle_book_returned,
    events.HoldUpdated: handle_hold_updated,
    # events.HoldRemoved: handle_hold_removed,
} 