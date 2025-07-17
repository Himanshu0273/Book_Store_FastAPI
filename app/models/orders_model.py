from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.enums import PaymentsEnum

if TYPE_CHECKING:
    from app.models.cart_model import Cart
    from app.models.payments_model import Payments
    from app.models.user_model import User


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="SET NULL"), nullable=True
    )

    cart_cost: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Float, nullable=False)
    taxes: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    payment_status: Mapped[PaymentsEnum] = mapped_column(
        SQLEnum(PaymentsEnum), default=PaymentsEnum.PENDING
    )

    user = relationship("User", back_populates="orders", passive_deletes=True)
    cart = relationship("Cart", back_populates="order", passive_deletes=True)
    payment = relationship("Payments", back_populates="order", uselist=False)
