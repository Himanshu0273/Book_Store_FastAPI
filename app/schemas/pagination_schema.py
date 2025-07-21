from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    data: List[T]
    next_cursor: Optional[int]=None
    