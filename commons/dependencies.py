from fastapi import Depends, Response
from sqlalchemy.orm import Session

from .config import CommonBaseConfig
from .redis_client import get_redis_client


def get_db_session_dependency(SessionLocal):
    def get_db_session():
        session: Session = SessionLocal()
        try:
            with session.begin():
                yield session
        finally:
            session.close()

    return get_db_session


def get_redis_dependency(config: CommonBaseConfig):
    def _get_redis_client():
        return get_redis_client(config)

    return _get_redis_client


def cache_control(ttl: int, is_public: bool):
    def cache_control_dependance(response: Response):
        response.headers["Cache-Control"] = f"public, max-age={ttl}" if is_public else f"max-age={ttl}"

    return Depends(cache_control_dependance)


