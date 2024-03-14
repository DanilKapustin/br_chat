from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional, Any, Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from uuid import uuid4

from chatbot.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from chatbot.db import get_db
from chatbot.db.model.user import User
from chatbot.dto.auth import TokenResult

logger = getLogger(__name__)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _get_password_hash(password) -> str:
    """Get password hash"""
    logger.debug("_get_password_hash")
    return password_context.hash(password)


async def get(db: AsyncSession, email: str) -> User:
    """Get user by email"""
    logger.debug("get, email=%s", email)
    return await db.scalar(select(User).filter(User.email == email))


async def create(db: AsyncSession, email: str, password: str) -> User:
    """Create user"""
    logger.debug("create, email=%s", email)

    hashed_password: str = _get_password_hash(password)
    user: User = User(id=uuid4(), email=email, hashed_password=hashed_password)
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def authenticate(
    db: AsyncSession, email: str, password: str
) -> Optional[TokenResult]:
    """Authenticate user"""
    logger.debug("authenticate, email=%s", email)

    user: Optional[User] = await get(db, email)

    if not user or not password_context.verify(password, user.hashed_password):
        return None

    access_token: str = _create_token(
        user.email, datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    result: TokenResult = TokenResult(access_token=access_token, token_type="bearer")

    return result


def _create_token(subject: str, expiration: datetime) -> str:
    """Create token"""
    logger.debug("_create_token, subject=%s, expiration=%s", subject, expiration)

    claim: dict = dict(sub=subject, exp=expiration)
    result: str = jwt.encode(claim, SECRET_KEY, algorithm=ALGORITHM)

    return result


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Get current user"""
    logger.debug("get_current_user, token=%s", token)
    credentials_exception: Exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user: User = await get(db, email=email)

    if not user:
        raise credentials_exception

    return user
