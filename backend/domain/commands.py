from attr import define

@define
class Command:
    pass

@define(frozen=True)
class AddBook(Command):
    name: str
    author: str
    isbn: str
    total_copies: int

@define(frozen=True)
class RemoveBook(Command):
    book_id: int

@define(frozen=True)
class CheckoutBook(Command):
    book_id: int
    user_id: int
    start_date: str | None = None
    end_date: str | None = None

@define(frozen=True)
class ReturnBook(Command):
    book_id: int
    user_id: int

@define(frozen=True)
class PlaceHold(Command):
    book_id: int
    user_id: int
    hold_date: str

@define(frozen=True)
class RemoveHold(Command):
    book_id: int
    user_id: int

@define(frozen=True)
class RegisterUser(Command):
    name: str
    username: str
    password: str
