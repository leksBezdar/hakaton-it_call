from typing import Generic, TypeVar
from pydantic import BaseModel


class SErrorMessage(BaseModel):
    error: str


IL = TypeVar("IL")


class SBaseQueryResponse(BaseModel, Generic[IL]):
    count: int
    limit: int
    offset: int
    items: IL
