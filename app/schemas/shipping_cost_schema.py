from typing import Optional

from pydantic import BaseModel, ConfigDict


class ShippingCostSchema(BaseModel):
    country: str
    cost: float

    model_config = ConfigDict(from_attributes=True)


class CreateShippingCost(ShippingCostSchema):
    pass


class ShowShippingCost(ShippingCostSchema):
    id: int


class UpdateShippingCost(BaseModel):
    country: Optional[str] = None
    cost: Optional[float] = None
