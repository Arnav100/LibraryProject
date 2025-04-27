from __future__ import annotations

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
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
            
        # Skip authentication for OPTIONS requests (preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        auth_header = request.headers.get('Authorization')
        print(auth_header)
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = auth_header.split(' ')[1]
        try:
            payload = verify_token(token)
        except HTTPException as e:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        with self.uow:
            user = self.uow.users.get(user_id)
            if user is None:
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"message": "User not found"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            request.state.user_id = user_id
            
        return await call_next(request)
