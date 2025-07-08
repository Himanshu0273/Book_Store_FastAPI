from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.genre_enum import GenreEnum

if TYPE_CHECKING:
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

    inventory = relationship(
        "Inventory", back_populates="book", uselist=False, cascade="all, delete-orphan"
    )

    # This is so that Quantity can be checked as part of the book table while using the show schema
    @property
    def quantity(self):
        return self.inventory.quantity if self.inventory else 0
