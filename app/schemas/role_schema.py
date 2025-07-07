from typing import Optional

from pydantic import BaseModel, ConfigDict


class RolesSchema(BaseModel):
    role_name: str
    model_config = ConfigDict(from_attributes=True)


class CreateRoles(RolesSchema):
    pass


class RolesUpdate(BaseModel):
    role_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ShowRoles(RolesSchema):
    id: int
