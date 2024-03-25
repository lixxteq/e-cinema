from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy import select

from application.models import User
from ..config import config
from ..main import db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])
jwt_auth_scheme = APIKeyCookie(name="access_token_cookie")

def credentials_exception(detail: str = 'Could not validate credentials'):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail
    )

async def _load_user(user_id) -> User | None:
    async for session in db.session():
        return await session.scalar(select(User).where(User.id == user_id))


async def current_user(jwt_token: str = Depends(jwt_auth_scheme)):
    user_id = None
    try:
        payload = jwt.decode(jwt_token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id = payload["sub"]
        if user_id is None:
            raise credentials_exception()
    except ExpiredSignatureError:
        raise credentials_exception('Token expired')
    except JWTError as error:
        raise error
    user = await _load_user(user_id)
    if user is None:
        raise credentials_exception('User not found')
    return user