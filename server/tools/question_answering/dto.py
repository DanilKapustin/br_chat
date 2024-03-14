from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Message create model"""

    message: str


class MessageRate(BaseModel):
    """Message rate model"""

    rating: int
