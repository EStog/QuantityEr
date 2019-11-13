from abc import abstractmethod
from datetime import datetime
from itertools import combinations
from typing import Iterable, Tuple, Set, Mapping

from lib.config.consts import SUBQUERY_NAME_FORMAT, QUOTE_FORMAT
from lib.internal_logic.caches.cache import Cache
from lib.internal_logic.translators.spaces_translator import SpacesTranslator
from lib.utilities.classes import WithArguments
from lib.utilities.enums import VerbosityLevel
from lib.utilities.functions import get_included_excluded_principle_iter_amount


class Engine(WithArguments):

    def __init__(self, cache: Cache, simulate: bool,
                 admit_incomplete: bool, **kwargs):
        super().__init__(**kwargs)
        self._cache = cache
        self._simulate = simulate
        self._admit_incomplete = admit_incomplete
        self._set_client()

    @abstractmethod
    def _set_client(self):
        pass

    def get_total_amount(self, query_name: str,
                         exp: str, symbols_table: Mapping[str, str]) -> \
            Tuple[int, int, int, int, int, int, datetime, datetime, datetime, datetime]:

        self._verbose_output(VerbosityLevel.DEBUG,
                             f'Getting results amount for query '
                             f'{QUOTE_FORMAT.format(query_name)} ...')
        backup_cache = {}
        if self._simulate:
            backup_cache = self._cache.copy()
        translator = SpacesTranslator()
        results = 0
        self._verbose_output(VerbosityLevel.DEBUG,
                             f'Getting total amount of subqueries '
                             f'for {QUOTE_FORMAT.format(query_name)} ...')
        subqueries_total = self.get_sub_queries_amount(exp)
        self._verbose_output(VerbosityLevel.INFO,
                             f'Subqueries amount for '
                             f'{QUOTE_FORMAT.format(query_name)}',
                             subqueries_total)

        estimated_time_min, estimated_time_max = self._estimated_time(subqueries_total)
        self._verbose_output(VerbosityLevel.INFO,
                             'Estimated time without caching for '
                             f'query {QUOTE_FORMAT.format(query_name)}',
                             f'from {estimated_time_min} to {estimated_time_max}')
        issued_subqueries = 0
        without_error_subqueries = 0
        with_error_to_be_substracted = 0
        with_error_to_be_added = 0
        i = 0

        if self._simulate:
            begin_run_datetime = datetime.now()
        else:
            begin_run_datetime = self._get_server_current_datetime()
        self._verbose_output(VerbosityLevel.INFO,
                             f'Server begin time for query {QUOTE_FORMAT.format(query_name)}',
                             begin_run_datetime)

        for query, sum_factor in self._get_subqueries(exp):
            query = translator.get_particular_query(query, symbols_table)
            i += 1
            subquery_name = SUBQUERY_NAME_FORMAT.format(query_name=query_name, i=i)
            self._verbose_output(VerbosityLevel.DEBUG,
                                 f'Subquery {QUOTE_FORMAT.format(subquery_name)} '
                                 f'of {subqueries_total}', query)
            if query not in self._cache:
                self._verbose_output(VerbosityLevel.DEBUG,
                                     f'Subquery {QUOTE_FORMAT.format(subquery_name)} '
                                     'to issue')
                if self._simulate:
                    sub_amount = 0
                    no_error = True
                else:
                    no_error, sub_amount = self._issue_query(subquery_name, query)
                if no_error:
                    self._cache[query] = sub_amount
                    self._verbose_output(VerbosityLevel.DEBUG,
                                         'Results amount cached for subquery '
                                         f'{QUOTE_FORMAT.format(subquery_name)}')
                    without_error_subqueries += 1
                else:
                    if sum_factor > 0:
                        with_error_to_be_added += 1
                    else:
                        with_error_to_be_substracted += 1
                issued_subqueries += 1
            else:
                self._verbose_output(VerbosityLevel.DEBUG,
                                     'Results amount for subquery '
                                     f'{QUOTE_FORMAT.format(subquery_name)} '
                                     'already cached')
                sub_amount = self._cache[query]
            self._verbose_output(VerbosityLevel.DEBUG,
                                 'Results amount for subquery '
                                 f'{QUOTE_FORMAT.format(subquery_name)}',
                                 sub_amount)
            results += sum_factor * sub_amount
        if self._simulate:
            end_run_datetime = datetime.now()
        else:
            end_run_datetime = self._get_server_current_datetime()
        self._verbose_output(VerbosityLevel.INFO,
                             f'Server end time for query {QUOTE_FORMAT.format(query_name)}',
                             end_run_datetime)

        self._verbose_output(VerbosityLevel.INFO,
                             'Runtime for query '
                             f'{QUOTE_FORMAT.format(query_name)}',
                             end_run_datetime - begin_run_datetime)

        if self._simulate:
            self._cache = backup_cache
        return (results, subqueries_total,
                issued_subqueries, without_error_subqueries,
                with_error_to_be_added, with_error_to_be_substracted,
                estimated_time_min, estimated_time_max,
                begin_run_datetime, end_run_datetime)

    def _get_subqueries(self, exp: str) -> Tuple[Set[str], int]:
        """This method implements an inclusion-exclusion principle"""
        query_list = exp.split(" | ")
        sum_factor = 1
        for p in range(1, len(query_list) + 1):
            for comb in combinations(query_list, p):
                yield self._get_conjunction_query(comb), sum_factor
            sum_factor *= -1

    @staticmethod
    def _get_conjunction_query(queries: Iterable[str]) -> Set[str]:
        conjunction_query = set()
        for query in queries:
            if query[0] == '(':
                query = query.strip()[1:-1]
            conjunction_query |= set(query.split(' & '))
        return conjunction_query

    @abstractmethod
    def _issue_query(self, name: str, query: str) -> Tuple[bool, int]:
        pass

    @abstractmethod
    def _estimated_time(self, subqueries_total: int) -> bool:
        pass

    @staticmethod
    def get_sub_queries_amount(exp: str) -> int:
        """This method implements an inclusion-exclusion principle"""
        query_list = exp.split(" | ")
        n = len(query_list)
        return get_included_excluded_principle_iter_amount(n)

    @abstractmethod
    def _get_server_current_datetime(self) -> datetime:
        pass


__all__ = ['Engine']
