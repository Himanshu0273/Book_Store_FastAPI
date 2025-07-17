from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.book_model import Book
from app.models.inventory_model import Inventory


class BookQueries:

    @staticmethod
    def get_all_books_query(db: Session) -> List[Book]:
        return db.query(Book).all()

    @staticmethod
    def get_book_by_id(book_id: int, db: Session) -> Book:
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def get_book_by_title(book_title: str, db: Session) -> Book:
        return db.query(Book).filter(Book.title == book_title).first()

    @staticmethod
    def get_books_by_author(author_name: str, db: Session) -> List[Book]:
        return db.query(Book).filter(Book.author.ilike(f"%{author_name}%"))

    @staticmethod
    def get_books_by_title(book_title: str, db: Session) -> List[Book]:
        return db.query(Book).filter(Book.title.ilike(f"%{book_title}%"))

    @staticmethod
    def sort_books_by_title_asc(db: Session) -> List[Book]:
        return db.query(Book).order_by(Book.title.asc()).all()

    @staticmethod
    def sort_books_by_title_desc(db: Session) -> List[Book]:
        return db.query(Book).order_by(Book.title.desc()).all()
