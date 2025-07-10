from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ShippingCost(Base):
    __tablename__ = "shipping_cost"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
