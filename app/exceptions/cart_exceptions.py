from fastapi import HTTPException, status


class CartNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The cart was not found!",
        )
        
        
class ItemQuantityLessThanZero(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The quantity should be positive",
        )