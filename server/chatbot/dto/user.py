from pydantic import BaseModel


class UserBase(BaseModel):
    """User base DTO"""

    email: str


class UserCreate(UserBase):
    """User create DTO"""

    password: str


class UserResult(UserBase):
    """User result DTO"""

    id: int

    class Config:
        orm_mode = True
