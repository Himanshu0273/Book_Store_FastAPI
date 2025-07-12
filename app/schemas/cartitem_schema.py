from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.book_schema import ShowBook


class CartItemSchema(BaseModel):
    book_id: int
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class CreateCartItem(CartItemSchema):
    pass


class ShowCartItem(CartItemSchema):
    id: int
    cart_id: int
    quantity: int
    price_when_added: float
    created_at: datetime
    updated_at: datetime | None = None
    book: ShowBook
