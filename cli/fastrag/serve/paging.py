from math import ceil
from typing import Literal, Protocol, Sequence

from attr import dataclass
from pydantic import BaseModel, Field, computed_field


class Paginated(Protocol):
    total: int
    page_size: int


def total_pages(page: Paginated) -> int:
    return ceil(page.total / page.page_size) if page.page_size else 0


class PageParameters(BaseModel):
    page: int = Field(
        1,
        ge=1,
        description="Page number (1-indexed)",
    )

    page_size: int = Field(
        10,
        ge=1,
        description="Number of items per page",
    )

    sort_by: str = Field(
        "created_at",
        description="Field to sort by",
    )

    sort_order: Literal["asc", "desc"] = Field(
        "desc",
        description="Sort order",
    )

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageResponse[T: BaseModel](BaseModel):
    """Base pagination class to use with BaseModels"""

    items: Sequence[T]
    total: int
    page: int
    page_size: int

    @computed_field
    @property
    def total_pages(self) -> int:
        return total_pages(self)


@dataclass
class Page[T]:
    """Base pagination class to use with SQLAlchemy models"""

    items: Sequence[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return total_pages(self)
