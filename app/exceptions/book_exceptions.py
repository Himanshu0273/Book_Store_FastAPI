from fastapi import HTTPException, status


class BookNotFound(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The book with ID: {book_id}, was not found!",
        )


class BookAlreadyExists(HTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The book with this title already exists: {book_title}",
        )
