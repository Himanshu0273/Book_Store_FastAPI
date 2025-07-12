from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.enums import GenreEnum

if TYPE_CHECKING:
    from app.models.cart_item_model import CartItem
    from app.models.inventory_model import Inventory


class Book(Base):

    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    genre: Mapped[GenreEnum] = mapped_column(SQLEnum(GenreEnum), nullable=False)
    desc: Mapped[str] = mapped_column(Text)
    year: Mapped[str] = mapped_column(String(4), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    added_on: Mapped[date] = mapped_column(Date, default=date.today)
    purchased: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    inventory = relationship(
        "Inventory", back_populates="book", uselist=False, cascade="all, delete-orphan"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    # This is so that Quantity can be checked as part of the book table while using the show schema
    @property
    def quantity(self):
        return self.inventory.quantity if self.inventory else 0

    # This can be avoided if I reference book.inventory directly whenever i want to change
    # @quantity.setter
    # def quantity(self, value):
    #     if self.inventory:
    #         self.inventory.quantity = value
    #     else:
    #         raise ValueError("Cannot set quantity because inventory is missing.")
