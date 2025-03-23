from typing import List
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError

import cattrs
from datetime import datetime, timedelta

from backend.adapters import orm
from backend.domain.models import Book, User, Checkout, Hold
from backend.service_layer.unit_of_work import UnitOfWork
from backend.service_layer import handlers
from backend.auth.utils import (
    verify_password, get_password_hash, create_access_token,
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
import uvicorn

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for these endpoints
        if request.url.path in ["/token", "/users"]:
            return await call_next(request)
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = auth_header.split(' ')[1]
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            
            with uow:
                user = uow.users.get(user_id)
                if user is None:
                    raise HTTPException(status_code=401, detail="User not found")
                request.state.user = user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return await call_next(request)

app = FastAPI()
app.add_middleware(AuthMiddleware)
orm.start_mappers()
uow = UnitOfWork()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with uow:
        user = uow.users.get_by_username(form_data.username)
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@app.get("/books")
async def get_books(request: Request):
    return handlers.get_books(uow)

@app.get("/books/{book_id}")
async def get_book(book_id, request: Request):
    return handlers.get_book(uow, book_id)
    
@app.post("/books")
async def add_book(book: dict, request: Request):
    return handlers.add_book(uow, book)

@app.get("/users")
async def get_users(request: Request):
    return handlers.get_users(uow)

@app.post("/users")
async def add_user(user: dict):
    user["password"] = get_password_hash(user["password"])
    return handlers.add_user(uow, user)

@app.get("/checkouts")
async def get_checkouts(request: Request):
    return handlers.get_checkouts(uow)

@app.post("/checkout")
async def checkout(user_id, book_id, request: Request):
    try: 
        return handlers.checkout(uow, user_id, book_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search")
async def search_book(title, request: Request):
    return handlers.search_book(uow, name=title)

@app.post("/hold")
async def place_hold(user_id, book_id, request: Request):
    try: 
        return handlers.place_hold(uow, user_id, book_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/hold")
async def remove_hold(hold_id, request: Request):
    try: 
        return handlers.remove_hold(uow, hold_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

uvicorn.run(app)