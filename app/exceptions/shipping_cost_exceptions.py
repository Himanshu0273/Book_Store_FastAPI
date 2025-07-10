from fastapi import HTTPException, status


class CountryNotFound(HTTPException):
    def __init__(self, country):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The country: {country} does not exist in the table!",
        )
