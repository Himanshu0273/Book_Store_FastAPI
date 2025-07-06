from fastapi import HTTPException, status


class DBException(HTTPException):
    def __init__(self,detail: str="Database Error", status_code = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(
            detail = detail,
            status_code = status_code
        )