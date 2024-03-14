from logging import getLogger
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.connection import get_db
from chatbot.db.model.user import User
from chatbot.dto.auth import TokenResult, Login
from chatbot.dto.user import UserResult, UserCreate
from chatbot.service import auth as service
from chatbot.util.error import BadRequestError

logger = getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/register", response_model=UserResult)
async def register(
    db: Annotated[AsyncSession, Depends(get_db)], user: UserCreate
) -> User:
    logger.debug("register, user=%s", user)
    result: Optional[User] = await service.get(db, user.email)

    if result is not None:
        raise BadRequestError("User already exists")

    result = await service.create(db, user.email, user.password)

    return result


@router.post("/token", response_model=TokenResult)
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form: Login,
) -> TokenResult:
    token: TokenResult = await service.authenticate(db, form.email, form.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@router.get("/me", response_model=UserResult)
async def get_current(
    user: Annotated[User, Depends(service.get_current_user)],
) -> User:
    return user
