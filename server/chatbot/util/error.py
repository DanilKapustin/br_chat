from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "Not found")


class BadRequestError(HTTPException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)
