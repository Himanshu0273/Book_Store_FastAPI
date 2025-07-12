from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.enums import CartActivityEnum

if TYPE_CHECKING:
    from app.models.cart_item_model import CartItem
    from app.models.orders_model import Order
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

    status: Mapped[CartActivityEnum] = mapped_column(
        SQLEnum(CartActivityEnum), default=CartActivityEnum.ACTIVE, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="cart")
    items: Mapped[List["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )

    order: Mapped["Order"] = relationship("Order", back_populates="cart", uselist=False)
