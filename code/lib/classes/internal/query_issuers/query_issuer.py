from abc import abstractmethod
from datetime import datetime
from typing import Tuple

from lib.utilities.logging.with_logging import WithLogging


class QueryIssuer(WithLogging):
    def __init__(self):
        WithLogging.__init__(self)
        self._query_name = ''
        self._set_client()

    @abstractmethod
    def _set_client(self):
        pass

    @abstractmethod
    def issue(self, name: str, query: str) -> Tuple[bool, int]:
        pass

    @abstractmethod
    def check_query_restrictions(self, query: str, name: str) -> bool:
        pass

    @abstractmethod
    def get_estimated_time(self, subqueries_total: int) -> bool:
        pass

    @abstractmethod
    def get_server_current_datetime(self) -> datetime:
        pass
