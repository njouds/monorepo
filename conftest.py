# type:ignore
import os
from importlib import import_module

import pytest
from celery import Celery
from commons.config import CommonBaseConfig
from commons.db import BaseDb
from commons.enums import AppName
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import scoped_session
from sqlalchemy_utils import create_database, drop_database

APP_NAME: str = os.getenv("APP_NAME")
if APP_NAME not in AppName.list():
    raise Exception(f" unknown app name ! {APP_NAME}")

config: CommonBaseConfig = import_module(f"{APP_NAME}.app.config").config
celery: Celery = import_module(f"{APP_NAME}.celery_worker.tasks").celery
app: FastAPI = import_module(f"{APP_NAME}.app.main").app
base_db = BaseDb(config)

get_db_read_session = import_module(f"{APP_NAME}.app.common.dependencies").get_db_read_session
get_db_session = import_module(f"{APP_NAME}.app.common.dependencies").get_db_session


ScopedSession = scoped_session(base_db.SessionLocal, scopefunc=lambda: "")


if APP_NAME == AppName.User.value:
    # User specific dependency_overrides
    pass


def get_celery_test_task():
    class TestCustomTask(celery.Task):
        _session = None
        _read_only_session = None
        _redis_client = None

        def before_start(self, *args, **kwargs):
            self._session = None
            self._read_only_session = None

        def after_return(self, *args, **kwargs):
            if self._session is not None:
                self._session.flush()
                # we can't expire_all here ,, because it will delete extra properties such as user in any object >_<
                # self._session.expire_all()

        @property
        def app_config(self):
            return config

        @property
        def session(self):
            if self._session is None:
                self._session = ScopedSession()
            return self._session

        @property
        def read_only_session(self):
            if self._read_only_session is None:
                self._read_only_session = ScopedSession()
            return self._read_only_session

    task = TestCustomTask

    return task


def get_db_session_overwrite():
    test_session = ScopedSession()
    test_session.expire_all()
    try:
        with test_session.begin_nested():
            yield test_session
    except Exception as e:
        import logging

        logging.exception(e, exc_info=True)


@pytest.fixture(autouse=True)
def transaction_flag():
    db_connection = base_db.engine.connect()
    db_connection.begin()
    ScopedSession(bind=db_connection)
    yield
    # so next time we create a session from ScopedSession
    # a new session will be created instead of using the same session
    ScopedSession.remove()
    db_connection.close()


@pytest.fixture()
def session():
    return ScopedSession()


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Create a Postgres database for the tests, and drop it when the tests are done.
    """

    app.dependency_overrides[get_db_session] = get_db_session_overwrite
    app.dependency_overrides[get_db_read_session] = get_db_session_overwrite

    try:
        create_database(base_db.engine.url)
    except Exception as e:
        print(e)

    os.chdir(f"./{APP_NAME}")
    os.system("alembic upgrade head")  # create all the tables

    celery.Task = get_celery_test_task()
    celery.conf["task_always_eager"] = True

    yield TestClient(app)

    base_db.engine.dispose()
    drop_database(base_db.engine.url)
