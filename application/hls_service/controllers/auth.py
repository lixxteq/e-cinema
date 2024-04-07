from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy import select

from ..exceptions import AuthorizationException
from application.models import User
from ..config import config
from ..main import db

router = APIRouter(prefix="/auth", tags=["auth"])
jwt_auth_scheme = APIKeyCookie(name="access_token_cookie", auto_error=False)

async def _load_user(user_id) -> User | None:
    async for session in db.session():
        return await session.scalar(select(User).where(User.id == user_id))

async def current_user(jwt_token: str = Depends(jwt_auth_scheme)):
    user_id = None
    if not jwt_token:
        raise AuthorizationException(detail="User not authenticated")
    try:
        payload = jwt.decode(jwt_token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id = payload["sub"]
        if user_id is None: # TODO: invalid value handler
            raise AuthorizationException(detail="Invalid token")
    except ExpiredSignatureError:
        raise AuthorizationException(detail="Token expired")
    except JWTError as error:
        raise error
    user = await _load_user(user_id)
    if user is None:
        raise AuthorizationException(detail="User not found")
    return user