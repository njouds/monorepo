from User.app.common.db import db
from User.app.config import config
from fastapi.security import OAuth2PasswordBearer
from app.api.user.exceptions import credentialsException
from typing import Optional
from jose import jwt, JWTError
from commons.dependencies import get_db_session_dependency, get_redis_dependency
from fastapi import Depends

get_db_read_session = get_db_session_dependency(db.ReadSessionLocal)
db_read_session = Depends(get_db_read_session)

get_db_session = get_db_session_dependency(db.SessionLocal)
db_session = Depends(get_db_session)

get_redis_client = get_redis_dependency(config=config)
redis_client = Depends(get_redis_client)


def get_verified_current_user_or_none(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="user/login", auto_error=False))
):
    if token is None:
        return None

    try:
        varified_and_decoded_token = jwt.decode(token, config.AUTH_JWT_KEY, algorithms=["HS256"])
    except JWTError:
        raise credentialsException

    return varified_and_decoded_token


def login_required(payload: Optional[dict] = Depends(get_verified_current_user_or_none)):
    """
    we are sure to have the token since we have auto_error = True
    """

    if payload is None:
        raise credentialsException
