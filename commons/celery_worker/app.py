import logging
from functools import wraps

from celery import Celery
from celery.app.task import Task
from commons.config import CommonBaseConfig
from commons.db import BaseDb
from commons.redis_client import RedisClient, get_redis_client
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import SessionTransaction

logger = logging.getLogger(__name__)


def stop_http_errors(func):
    @wraps(func)
    def new_func(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except HTTPException as e:
            raise Exception(f"HTTPException: code: {e.status_code}, detail: {e.detail}")

    return new_func


class CustomTask(Task):
    app_config: CommonBaseConfig
    session: Session
    read_only_session: Session
    redis_client: RedisClient
    transaction: SessionTransaction


def init_app(config: CommonBaseConfig):
    base_db = BaseDb(config)

    backend = config.CELERY_RESULT_BACKEND
    if backend is None:
        backend = config.CELERY_BROKER_URL

    client = Celery(
        config.APP_NAME,
        backend=backend if config.CELERY_ENABLE_RESULT_BACKEND else None,
        borker=config.CELERY_BROKER_URL,
    )

    class FullCustomTask(CustomTask):
        _session: Session | None = None
        _read_only_session: Session | None = None
        _redis_client: RedisClient | None = None
        transaction: SessionTransaction

        def before_start(self, *args, **kwargs):
            if config.testing:
                raise Exception("THIS IS NOT TEST TASK, tests must use there own custom task")

        def after_return(self, *args, **kwargs):
            if self._session is not None:
                self._session.commit()
                self._session.close()
                self._session = None
            if self._read_only_session is not None:
                self._read_only_session.close()
                self._read_only_session = None

        @property
        def app_config(self):
            return config

        @property
        def session(self):
            if self._session is None:
                self._session = base_db.SessionLocal()
                self.transaction = self._session.begin()
            return self._session

        @property
        def read_only_session(self):
            if self._read_only_session is None:
                self._read_only_session = base_db.ReadSessionLocal()
            return self._read_only_session

        @property
        def redis_client(self):
            if self._redis_client is None:
                self._redis_client = get_redis_client(config)
            return self._redis_client

        priority = 9
        autoretry_for = (Exception,) if config.ENABLE_CELERY_RETRY else tuple()
        retry_backoff = True if config.ENABLE_CELERY_RETRY_BACKOFF else False
        max_retries = config.CELERY_RETRY_MAX
        retry_backoff_max = config.CELERY_RETRY_BACKOFF_MAX

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            if isinstance(exc, HTTPException):
                exc = Exception(f"HTTPException: code: {exc.status_code}, detail: {exc.detail}")
            logger.exception(exc, exc_info=True)
            if self._session is not None:
                self._session.close()
                self._session = None
            super().on_failure(exc, task_id, args, kwargs, einfo)

        def on_retry(self, exc, task_id, args, kwargs, einfo):
            if self._session is not None:
                self._session.close()
                self._session = None
            if self._read_only_session is not None:
                self._read_only_session.close()
                self._read_only_session = None
            return super().on_retry(exc, task_id, args, kwargs, einfo)

    client.Task = FullCustomTask

    return client
