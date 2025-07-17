from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.permissions import is_admin
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions.book_exceptions import (AuthorNotPresent,
                                            BookAlreadyExists, BookNotFound)
from app.exceptions.db_exception import DBException
from app.models.book_model import Book
from app.models.inventory_model import Inventory
from app.models.user_model import User
from app.queries.book_queries import BookQueries
from app.schemas.book_schema import (CreateBook, ShowBook, UpdateBook,
                                     UpdateInventory)
from app.utils.response import build_response

book_router = APIRouter(prefix="/books", tags=["Book"])


# Add book
@book_router.post("/add-new-book", status_code=status.HTTP_201_CREATED)
def add_book_details(
    request: CreateBook,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    func_logger.info("POST - /books/add-new-book")
    if BookQueries.get_book_by_title(book_title=request.title, db=db):
        raise BookAlreadyExists(request.title)

    try:

        new_book = Book(
            title=request.title,
            author=request.author,
            genre=request.genre,
            desc=request.desc,
            year=request.year,
            price=request.price,
            image=request.image,
        )

        db.add(new_book)
        db.flush()

        new_inventory = Inventory(book_id=new_book.id, quantity=request.quantity)

        db.add(new_inventory)
        db.commit()
        db.refresh(new_book)
        func_logger.info("Book added successfully!!")

        return build_response(
            status_code=status.HTTP_201_CREATED,
            payload=new_book,
            message="Book and inventory added successfully",
        )

    except Exception as e:
        db.rollback()
        func_logger.error(f"DB Error while adding book: {e}")
        raise DBException()


# Get All books
@book_router.get("/get-all-books", status_code=status.HTTP_200_OK)
def get_all_books(db: Session = Depends(get_db)):
    func_logger.info("GET - book/get-all-books")

    books = BookQueries.get_all_books_query(db=db)

    response_books: List[ShowBook] = []
    response_books = [ShowBook.model_validate(book) for book in books]
    return build_response(
        status_code=status.HTTP_200_OK,
        payload=response_books,
        message="These are all the books in the Library!",
    )


# Get book by id
@book_router.get("/get-book-by-id/{id}", status_code=status.HTTP_200_OK)
def get_book_by_id(id: int, db: Session = Depends(get_db)):

    func_logger.info(f"GET - /books/get-book-by-id/{id}")

    book = BookQueries.get_book_by_id(book_id=id, db=db)
    if not book:
        func_logger.error(f"No Book with id: {id} found!")
        raise BookNotFound(book_id=id)

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=ShowBook.model_validate(book),
        message=f"The book with given ID is found: {id}",
    )


# Get book by author
@book_router.get("/get-books-by-author/{author_name}", status_code=status.HTTP_200_OK)
def get_book_by_author(author_name: str, db: Session = Depends(get_db)):

    func_logger.info(f"GET - /books/get-books-by-author/{author_name}")

    books = BookQueries.get_books_by_author(author_name=author_name, db=db)

    if not books:
        func_logger.error(f"Books for the given author not present: {author_name}")
        raise AuthorNotPresent(author_name=author_name)

    response_books = [ShowBook.model_validate(book) for book in books]

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=response_books,
        message=f"These are all the books by author: {author_name}",
    )


# Get book by title
@book_router.get("/get-books-by-title/{book_title}", status_code=status.HTTP_200_OK)
def get_book_by_title(book_title: str, db: Session = Depends(get_db)):
    func_logger.info(f"GET - /books/get-books-by-title/{book_title}")

    # books = BookQueries.get_books_by_author(author_name=author_name, db=db)
    books = BookQueries.get_books_by_title(book_title=book_title, db=db)
    if not books:
        func_logger.error(f"Books for the given title not present: {book_title}")
        raise BookNotFound(book_id=404)

    response_books = [ShowBook.model_validate(book) for book in books]

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=response_books,
        message=f"These are all the books of title: {book_title}",
    )


# Sort books by title in asc
@book_router.get("/sort-books-by-title-asc", status_code=status.HTTP_200_OK)
def sort_books_asc(db: Session = Depends(get_db)):
    func_logger.info("GET - /books/sort-books-by-title-asc")

    books = BookQueries.sort_books_by_title_asc(db=db)
    if not books:
        func_logger.error("No books found to sort by title ascending.")
        raise BookNotFound(book_id=0)

    response_books = [ShowBook.model_validate(book) for book in books]

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=response_books,
        message="Books sorted by title in ascending order",
    )


# Sort books by title in desc
@book_router.get("/sort-books-by-title-desc", status_code=status.HTTP_200_OK)
def sort_books_asc(db: Session = Depends(get_db)):
    func_logger.info("GET - /books/sort-books-by-title-desc")

    books = BookQueries.sort_books_by_title_desc(db=db)
    if not books:
        func_logger.error("No books found to sort by title descending.")
        raise BookNotFound(book_id=0)

    response_books = [ShowBook.model_validate(book) for book in books]

    return build_response(
        status_code=status.HTTP_200_OK,
        payload=response_books,
        message="Books sorted by title in descending order",
    )


# Update book info
@book_router.put("/update-book/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_book_details(
    id: int,
    request: UpdateBook,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    func_logger.info(f"PUT - /books/update_book/{id}")

    book = BookQueries.get_book_by_id(book_id=id, db=db)
    if not book:
        raise BookNotFound(book_id=id)
    try:
        update_book = request.model_dump(exclude_unset=True)
        for key, value in update_book.items():
            setattr(book, key, value)

        db.commit()
        db.refresh(book)
        return build_response(
            status_code=status.HTTP_202_ACCEPTED,
            payload=ShowBook.model_validate(book),
            message=f"Role Updated successfully!\nid:{id}",
        )

    except Exception as e:
        db.rollback()
        func_logger.error(f"DB Error during updating book details: {e}")
        raise DBException()


# update inventory for a book using its ID
@book_router.patch("/books/update-inventory/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_inventory(
    book_id: int,
    request: UpdateInventory,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    func_logger.info(f"PATCH - /books/update-inventory/{book_id}")

    inventory = db.query(Inventory).filter(Inventory.book_id == book_id).first()

    if not inventory:
        func_logger.error(f"The book was not found: {book_id}")
        raise BookNotFound(book_id=book_id)

    try:
        if request.quantity is not None:
            inventory.quantity = request.quantity

        db.commit()
        db.refresh(inventory)
        return {
            "message": "Inventory updated successfully",
            "book_id": book_id,
            "quantity": inventory.quantity,
        }

    except Exception as e:
        db.rollback()
        func_logger.error("Error in DB when updating Inventory")
        raise DBException()


# Delete book
@book_router.delete("/books/delete-book/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(is_admin)
):
    func_logger.info(f"DELETE - /books/delete-book/{id}")

    book = BookQueries.get_book_by_id(book_id=id, db=db)
    if not book:
        raise BookNotFound(book_id=id)

    try:
        db.delete(book)
        db.commit()

        return

    except Exception as e:
        db.rollback()
        func_logger.error("DB Error while deleting book")
        raise DBException()
