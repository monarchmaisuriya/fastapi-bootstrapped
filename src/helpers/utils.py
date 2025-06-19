from typing import Any, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from starlette.responses import JSONResponse

T = TypeVar("T")


# Custom error class for exceptions with status code support
class APIError(Exception):
    def __init__(
        self, status_code: int = 500, error: str = "An unknown error occurred"
    ):
        self.status_code = status_code
        self.error = error

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"error": self.error, "status_code": self.status_code},
        )


# Standardized response model for consistent API responses
class APIResponse(BaseModel, Generic[T]):
    data: T | None = None
    meta: dict[str, Any] | None = None


# Pagination parameters for pagination
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=100, description="Page size"),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


# Search parameters for search
class SearchParams:
    def __init__(
        self,
        search: str | None = Query(None, min_length=1, description="Search term"),
        order_by: str | None = Query(None, description="Order by field"),
        is_active: bool | None = Query(None, description="Filter by active status"),
    ):
        self.search = search
        self.order_by = order_by
        self.is_active = is_active
