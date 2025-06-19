from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from helpers.auth import verify_access_token
from helpers.utils import APIError


class AuthenticateRequest(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, public_paths=None):
        super().__init__(app)
        self.public_paths = public_paths or set()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            if request.url.path in self.public_paths:
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise APIError(401, "Missing or invalid Authorization header")

            token = auth_header.split("Bearer ")[-1]
            payload = verify_access_token(token)
            request.state.user = payload  # type: ignore[attr-defined]
            return await call_next(request)

        except APIError as e:
            return e.to_response()
