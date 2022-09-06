import logging
import os
from functools import lru_cache

from pydantic import BaseSettings

from .enums import LoggingLevel

logger = logging.getLogger(__name__)


POSTGRES_CONNECTION = "postgresql://{user}:{password}@{host}:{port}/{database}"


class CommonBaseConfig(BaseSettings):
    production: bool = False
    testing: bool = False
    ENVIRONMENT: str = "default"
    default_allow_origins = ["*"]
    APP_NAME: str = "common"
    ALLOWED_HOSTS: list[str] = ["*"]

    FORWARDED_ALLOW_IPS: str = "*"

    @property
    def allow_hosts(self):
        """
        a,b,c => ['a','b','c']
        """
        if os.environ.get("ALLOWED_HOSTS") is None:
            return self.default_allow_origins
        else:
            return os.environ.get("ALLOWED_HOSTS").split(",")

    @property
    def allow_core_origins(self):
        if os.environ.get("ALLOWED_CORS_ORIGINS") is None:
            return self.default_allow_origins
        else:
            return os.environ.get("ALLOWED_CORS_ORIGINS").split(",")

    # to disable docs if = None
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"

    # email configs
    SMTP_SENDER: str = ""
    SMTP_SENDERNAME: str = ""
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_HOST: str | None = None
    SMTP_TIMEOUT: float = 60
    SMTP_PORT: int | None = None

    # db configs
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

    # read only db configs
    READ_ONLY_DB_USER: str | None
    READ_ONLY_DB_PASSWORD: str | None
    READ_ONLY_DB_NAME: str | None
    READ_ONLY_DB_HOST: str | None
    READ_ONLY_DB_PORT: int | None

    # rides configs
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_DB: int | None = None
    REDIS_CASHING_TTL: int = 3600
    REDIS_LOCAL_CASHING_TTL: int = 2
    REDIS_LOCAL_CASH_SIZE_LIMIT: int = 1000
    REDIS_TIMEOUT: int = 500
    REDIS_CONNECTION_POOL_SIZE: int = 20
    REDIS_SOCKET_KEEPALIVE: bool = True

    ENABLE_CASHING: bool = True

    # celery configs
    CELERY_RESULT_BACKEND: str | None = None
    CELERY_BROKER_URL: str
    ENABLE_CELERY_RETRY: bool = True
    ENABLE_CELERY_RETRY_BACKOFF: bool = True
    CELERY_RETRY_MAX: int = 10
    CELERY_RETRY_BACKOFF_MAX: int = 3600
    CELERY_ENABLE_RESULT_BACKEND: bool = False

    # logging level ,,
    LOGGING_LEVEL: LoggingLevel = LoggingLevel.INFO

    # the current head git sha ,, used to track deployments
    RELEASE_SHA: str = "unknown"

    # generate SQLALCHEMY_DATABASE_URL dynamically
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return POSTGRES_CONNECTION.format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    @property
    def SQLALCHEMY_READ_DATABASE_URL(self) -> str:
        if self.READ_ONLY_DB_USER is not None:
            return POSTGRES_CONNECTION.format(
                user=self.READ_ONLY_DB_USER,
                password=self.READ_ONLY_DB_PASSWORD,
                host=self.READ_ONLY_DB_HOST,
                port=self.READ_ONLY_DB_PORT,
                database=self.READ_ONLY_DB_NAME,
            )
        else:
            return self.SQLALCHEMY_DATABASE_URL

    SQL_POOL_SIZE: int = 40
    SQL_POOL_OVERFLOW_SIZE: int = 10
    SQL_POOL_ENABLED: bool = True

    class Config:
        env_file = ".env"


# you can set the defaults from here or over ride all using .env


class CommonProductionConfig(BaseSettings):
    production = True
    testing = False
    ENVIRONMENT = "prod"
    openapi_url: str | None = None


class CommonStagingConfig(BaseSettings):
    production = True
    testing = False
    ENVIRONMENT = "staging"
    LOGGING_LEVEL: LoggingLevel = LoggingLevel.DEBUG


class CommonTestingConfig(BaseSettings):
    production = False
    testing = True
    ENVIRONMENT = "testing"
    SQL_POOL_ENABLED = False


@lru_cache()
def current_config(ProductionConfig, StagingConfig, TestingConfig, BaseConfig):
    """
    this will load the required config passed on STAGE env if not set it will load LocalConfig
    """
    stage = os.environ.get("ENVIRONMENT", "local")
    stage_to_config_map = {
        "prod": ProductionConfig,
        "staging": StagingConfig,
        "testing": TestingConfig,
        "local": BaseConfig,
    }
    if stage not in stage_to_config_map:
        raise Exception(f"ENVIRONMENT: {stage} is not supported")

    logger.info(f"loading {stage} Config...")
    return stage_to_config_map[stage]()
