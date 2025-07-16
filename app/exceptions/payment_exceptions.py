from fastapi import HTTPException, status


class PaymentNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The payment was not found!",
        )
        
class AttemptsExceeded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have exceeded the number of valid attempts: (3)"
        )
        
class TransactionNotAdded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't add the transaction due to some internal issues"
        )