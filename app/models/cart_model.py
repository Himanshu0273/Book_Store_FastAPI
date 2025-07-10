from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.cart_item_model import CartItem
    from app.models.user_model import User


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_books: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="cart")
    items: Mapped[List["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )
