from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CartSchema(BaseModel):
    total_books: int
    total_cost: float

    model_config = ConfigDict(from_attributes=True)


class ShowCart(CartSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
