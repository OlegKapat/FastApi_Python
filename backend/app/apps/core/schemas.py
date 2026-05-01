from enum import IntEnum, StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IdSchema(BaseModel):
    id: int = Field(description="Unique identifier", gt=0)


class InstanceVersion(BaseModel):
    version: int = Field(examples=[1, 2], gt=0)


class PaginationResponseSchema(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    pages: int = 1


class PaginationParamsEnum(IntEnum):
    MAX_RESULT_PER_PAGE = 50
    DEFAULT_RESULT_PER_PAGE = 10
    MIN_RESULTS_PER_PAGE = 1


class SortEnum(StrEnum):
    ASC = "asc"
    DESC = "desc"


class SortFieldEnum(StrEnum):
    ID = "id"
    UPDATED_AT = "updated_at"


class SearchParamSchema(BaseModel):
    q: Optional[str] = Field(None, description="Search query")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(
        default=PaginationParamsEnum.DEFAULT_RESULT_PER_PAGE.value,
        le=PaginationParamsEnum.MAX_RESULT_PER_PAGE.value,
        ge=PaginationParamsEnum.MIN_RESULTS_PER_PAGE.value,
    )
    sort_direction: SortEnum = SortEnum.ASC
    sort_by: SortFieldEnum = SortFieldEnum.ID
    use_sharp_filter: bool = Field(
        default=False, description="Use sharp filter for search"
    )
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("q")
    def normalize_q(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        return v.lower()
