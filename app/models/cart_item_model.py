from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.book_model import Book
    from app.models.cart_model import Cart


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer)
    price_when_added: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=False
    )

    book: Mapped["Book"] = relationship(back_populates="cart_items")
    cart: Mapped["Cart"] = relationship(back_populates="items")
