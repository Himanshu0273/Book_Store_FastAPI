from fastapi import HTTPException, status


class OrderNotFound(HTTPException):
    def __init__(self, order_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order with ID: {order_id} was not found!!",
        )
