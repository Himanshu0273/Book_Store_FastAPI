from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.utils.enums import GenreEnum


class BookSchema(BaseModel):

    title: str
    author: str
    genre: GenreEnum
    desc: str
    year: str
    price: float
    image: str

    model_config = ConfigDict(from_attributes=True)


class CreateBook(BookSchema):
    quantity: int


class UpdateBook(BaseModel):

    title: Optional[str] = None
    author: Optional[str] = None
    desc: Optional[str] = None
    year: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None


class ShowBook(BookSchema):
    id: int
    quantity: int
    avg_rating: Optional[float]
    added_on: date


# Update Inventory for a book
class UpdateInventory(BaseModel):
    quantity: Optional[int] = None
