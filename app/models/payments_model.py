from sqlalchemy import ForeignKey, Integer, Float,  Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime, timezone
from app.db.base import Base
from typing import TYPE_CHECKING, List
from app.utils.enums import PaymentsEnum, PaymentMethodEnum

if TYPE_CHECKING:
    from app.models.orders_model import Order
    from app.models.transaction_model import Transactions

class Payments(Base):
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable = False)
    total_cost: Mapped[float] = mapped_column(Float)
    mode_of_payment: Mapped[PaymentMethodEnum] = mapped_column(SQLEnum(PaymentMethodEnum))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PaymentsEnum] = mapped_column(SQLEnum(PaymentsEnum))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    
    order: Mapped["Order"] = relationship(back_populates="payment")
    transactions: Mapped[List["Transactions"]] = relationship(back_populates="payment", cascade="all, delete-orphan")
    