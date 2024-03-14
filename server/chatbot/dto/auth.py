from pydantic import BaseModel


class Login(BaseModel):
    """Login DTO"""

    email: str
    password: str


class TokenResult(BaseModel):
    """Token result DTO"""

    access_token: str
    token_type: str
