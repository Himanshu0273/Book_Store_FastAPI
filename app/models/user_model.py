from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.db.base import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.roles_model import Roles
    
class User(Base):
    __tablename__="users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False) 
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    
    role: Mapped["Roles"] = relationship("Roles", back_populates="users")