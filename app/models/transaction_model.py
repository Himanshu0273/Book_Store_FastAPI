import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.enums import TransactionStatusEnum

if TYPE_CHECKING:
    from app.models.payments_model import Payments


class Transactions(Base):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), nullable=False)
    txn_reference: Mapped[str] = mapped_column(
        nullable=False, default=lambda: str(uuid.uuid4())
    )
    status: Mapped[TransactionStatusEnum] = mapped_column(
        SQLEnum(TransactionStatusEnum), nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    payment: Mapped["Payments"] = relationship(back_populates="transactions")
