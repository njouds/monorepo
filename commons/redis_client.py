import copy
import logging
from threading import Lock
from typing import Any

import orjson
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from redis import Redis

from .config import CommonBaseConfig

logger = logging.getLogger(__name__)

global_redis_client = None


def _copy_cached_data(*arg, **kwargs):
    """
    apply the `cached` decorator but return a copy of the value so we don't effect it.
    ie: this is a work around passing the value by reference
    """
    old_outer_wrapper = cached(*arg, **kwargs)

    def outer_wrapper(func):
        old_inner_wrapper = old_outer_wrapper(func)

        def wrapper(*arg1, **kwargs2):
            result = old_inner_wrapper(*arg1, **kwargs2)
            return copy.deepcopy(result)

        return wrapper

    return outer_wrapper


JSONType = str | int | float | bool | None | dict[str, Any] | list[Any]


class RedisClient(object):
    """this is for typing only"""

    client: Redis | None = None

    def cache_data(self, key: str, data, ex=-1) -> bool | None:
        return None

    def get_data(self, key) -> JSONType:
        return None

    def mget_data(self, keys: list[str]) -> list[JSONType] | None:
        return None

    def clear_cache(self, *keys) -> int | None:
        return None

    def clear_all_data(self):
        return None


def get_redis_client(config: CommonBaseConfig):
    global global_redis_client
    if global_redis_client is not None:
        return global_redis_client

    local_cash: TTLCache = TTLCache(
        maxsize=config.REDIS_LOCAL_CASH_SIZE_LIMIT,
        ttl=config.REDIS_LOCAL_CASHING_TTL,
    )
    lock = Lock()

    def is_redis_enabled():
        return config.REDIS_HOST is not None and config.ENABLE_CASHING

    class RealRedisClient(RedisClient):
        client: Redis

        def __init__(self):
            self.enable_cashing = config.ENABLE_CASHING
            self.redis_ttl = config.REDIS_CASHING_TTL
            self.local_ttl = config.REDIS_LOCAL_CASHING_TTL
            self.local_cash_size_limit = config.REDIS_LOCAL_CASH_SIZE_LIMIT
            self.client = Redis(
                db=config.REDIS_DB,
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                socket_timeout=config.REDIS_TIMEOUT,
                socket_connect_timeout=config.REDIS_TIMEOUT,
                max_connections=config.REDIS_CONNECTION_POOL_SIZE,
                socket_keepalive=config.REDIS_SOCKET_KEEPALIVE,
            )

        def cache_data(self, key: str, data, ex=-1):
            # override set ttl to avoid infinite ttl
            if ex == -1:
                ex = self.redis_ttl

            with lock:
                local_cash.pop(hashkey(self, key), None)

            if self.enable_cashing and self.client is not None:
                try:
                    json = orjson.dumps(data)
                    return self.client.set(key, json, ex)
                except Exception as e:
                    logger.warning(f"cache throw an error ! {e}")

        @_copy_cached_data(cache=local_cash, key=hashkey, lock=lock)
        def get_data(self, key) -> dict | None:
            if not isinstance(key, str):
                key = str(key)

            try:
                res = self.client.get(key)
            except Exception as e:
                logger.warning(f"redis throw for key:{key} an error ! {e}")
                res = None

            if res is None:
                return None

            return orjson.loads(res)

        def mget_data(self, keys: list[str]) -> list[JSONType]:
            data_list = list(map(self._get_data_locally, keys))
            none_keys = [key for key, data in zip(keys, data_list) if data is None]

            if len(none_keys) == 0:
                return data_list

            try:
                res = self.client.mget(none_keys)
            except Exception:
                res = list(map(lambda x: None, none_keys))

            def decode_and_cache_local(res):
                if res is not None:
                    decoded_data = orjson.loads(res)
                    local_cash.__setitem__(key, decoded_data)
                    return decoded_data

            # used to replace None valued keys in their exact index
            for key, data in zip(none_keys, res):
                index = keys.index(key)
                data_list[index] = decode_and_cache_local(data)

            return data_list

        def _get_data_locally(self, key):
            if local_cash is None:
                return None
            with lock:
                return local_cash.get(hashkey(key), None)

        def clear_cache(self, *keys):
            if local_cash is not None:
                local_cash.clear()

            keys = [str(key) for key in keys]
            return self.client.delete(*keys)

        def clear_all_data(self):
            local_cash.clear()
            self.client.flushdb()

    global_redis_client = RealRedisClient() if is_redis_enabled() else RedisClient()
    return global_redis_client
