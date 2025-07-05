from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Integer, String
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_model import User
    
class Roles(Base):
    __tablename__="roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    users: Mapped[list["User"]] = relationship("User", back_populates="role", cascade="all, delete", passive_deletes=True)