from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    email: str
    role_id: int
    country: str
    
    model_config=ConfigDict(from_attributes=True)
    
class CreateUser(UserSchema):
    password: str
    
class ShowUser(UserSchema):
    id: int
    created_at: datetime

class UpdateUser(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    country: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)