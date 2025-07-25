from typing import List
from fastapi import FastAPI, HTTPException, Depends, status, Request, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from contextlib import asynccontextmanager

from backend import bootstrap
from backend.entrypoint.middleware.auth import AuthMiddleware
from backend.domain import commands
from backend.service_layer import views
from backend.auth.utils import (
    verify_password, get_password_hash, create_access_token,
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.entrypoint.connection_manager import ConnectionManager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await manager.start()
    yield
    # Shutdown
    await manager.stop()

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bus = bootstrap.bootstrap()
app.add_middleware(AuthMiddleware, uow=bus.uow)

manager = ConnectionManager(bus=bus)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.middleware("http")
async def handle_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(content={"message": e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with bus.uow:
        user = bus.uow.users.get_by_username(form_data.username)
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
    return views.BookView.get_all(bus.uow)


@app.get("/books/{book_id}")
async def get_book(book_id: int, request: Request):
    book = views.BookView.get_by_id(bus.uow, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
    
# use kafka to publish events, setup locally  
# Make sure commands are agnostic to kafka   
# Use docker container for kafka

@app.post("/books")
async def add_book(book: dict, request: Request):
    cmd = commands.AddBook(
        name=book["name"],
        author=book["author"],
        isbn=book["isbn"],
        total_copies=book["total_copies"],
        cover_url=book["cover_url"],
        description=book["description"]
    )
    return bus.handle(cmd)

@app.get("/users")
async def get_users(request: Request):
    return views.UserView.get_all(bus.uow)

@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    user = views.UserView.get_by_id(bus.uow, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/user/me")
async def get_current_user(request: Request):
    user_id = request.state.user_id
    user = views.UserView.get_by_id(bus.uow, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users")
async def add_user(user: dict):
    cmd = commands.RegisterUser(
        name=user["name"],
        username=user["username"],
        password=user["password"]
    )
    return bus.handle(cmd)

@app.get("/checkouts")
async def get_checkouts(request: Request):
    return views.CheckoutView.get_all(bus.uow)

@app.get("/checkouts/me")
async def get_checkouts(request: Request):
    user_id = request.state.user_id
    return views.CheckoutView.get_by_user(bus.uow, user_id)

@app.post("/checkout")
async def checkout(user_id, book_id, request: Request):
    try: 
        cmd = commands.CheckoutBook(
            user_id=user_id,
            book_id=book_id
        )
        return bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/return")
async def return_book(checkout_id, request: Request):
    try: 
        cmd = commands.ReturnBook(
            checkout_id=checkout_id
        )
        return bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search")
async def search_book(title: str, request: Request):
    return views.BookView.search(bus.uow, title)

@app.get("/holds")
async def get_holds(request: Request):
    return views.HoldView.get_all(bus.uow)

@app.get("/holds/me")
async def get_holds(request: Request):
    user_id = request.state.user_id
    return views.HoldView.get_by_user(bus.uow, user_id)

@app.post("/hold")
async def place_hold(user_id, book_id, request: Request):
    try: 
        cmd = commands.PlaceHold(
            user_id=user_id,
            book_id=book_id
        )
        return bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/hold")
async def remove_hold(hold_id, request: Request):
    try: 
        cmd = commands.RemoveHold(
            hold_id=hold_id
        )
        return bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f"Connecting websocket for user {user_id}")
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

uvicorn.run(app)