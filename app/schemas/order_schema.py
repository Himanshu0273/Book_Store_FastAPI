from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.utils.enums import PaymentsEnum


class CreateOrderSchema(BaseModel):
    shipping_address: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class ShowOrderSchema(BaseModel):
    id: int
    cart_id: int
    user_id: int
    cart_cost: float
    shipping_cost: float
    taxes: float
    total: float
    shipping_address: str
    country: str
    date: datetime
    payment_status: PaymentsEnum

    model_config = ConfigDict(from_attributes=True)


class UpdateOrderSchema(BaseModel):
    shipping_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
