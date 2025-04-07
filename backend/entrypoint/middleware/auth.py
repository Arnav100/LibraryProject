from __future__ import annotations

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from backend.service_layer.unit_of_work import UnitOfWork
from backend.auth.utils import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, uow: UnitOfWork):
        super().__init__(app)
        self.uow = uow

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
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            
        with self.uow:
            user = self.uow.users.get(user_id)
            if user is None:
                raise HTTPException(status_code=401, detail="User not found")
            request.state.user = user
            
        return await call_next(request)
