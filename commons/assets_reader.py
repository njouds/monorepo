from pathlib import Path
from typing import Any

import yaml


class AssetsReader(object):
    """
    this services will read assets and cash them so they can be called every were with no issues
    """

    data_cash: dict[str, Any] = {}

    @classmethod
    def read_yaml(cls, file_name: str):
        """
        read a file from commons/assets/{file_name}
        """

        cash_key = f"read_yaml:{file_name}"
        data = cls.data_cash.get(cash_key)
        if data is not None:
            return data

        path = Path(__file__).parent / f"./assets/{file_name}"
        # Don't use asynchronous code here, adds to complexity with little to unknown value, not worth it.
        with path.open(mode="rt", encoding="utf8") as file:
            data = yaml.safe_load(file)
            cls.data_cash[cash_key] = data
            return data

    @classmethod
    def read_string(cls, file_name: str) -> str:
        cash_key = f"read_string:{file_name}"
        data = cls.data_cash.get(cash_key)
        if data is not None:
            return data

        path = Path(__file__).parent / f"./assets/{file_name}"
        with path.open(mode="rt", encoding="utf8") as file:
            data = file.read()
            cls.data_cash[cash_key] = data
            return data
