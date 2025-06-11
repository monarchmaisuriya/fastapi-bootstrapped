from typing import Any

from fastapi import HTTPException, Query
from pydantic import BaseModel


# Custom error class for exceptions with status code support
class APIError(HTTPException):
    def __init__(
        self, status_code: int = 500, error: str = "An unknown error occurred"
    ):
        self.error = error
        self.message = {"error": error, "status_code": status_code}
        super().__init__(status_code=status_code, detail=error)


# Standardized response model for consistent API responses
class APIResponse(BaseModel):
    data: dict[str, Any] | str | bytes | list | None = None


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
