import time
from itertools import combinations
from abc import abstractmethod
from typing import Optional, Iterable, FrozenSet, Tuple, Union

import github
from github import Github, RateLimitExceededException, \
    BadCredentialsException, GithubException
from requests import ConnectionError

from lib.utilities.classes import WithDefaults
from lib.utilities.enums import XEnum, VerbosityLevel, ExitCode
from lib.utilities.functions import cast_tuple_from_str, normalize_name, \
    get_waiting_time, get_included_excluded_principle_iter_amount, get_time_prognostic
from lib.internal_logic.translators import SpacesTranslator
from lib.utilities.flip_dict import Flipdict


class Engine(WithDefaults):

    def __init__(self, simulate: bool,
                 admit_incomplete: bool):
        super().__init__()
        self._simulate = simulate
        self._admit_incomplete = admit_incomplete
        self._cache = dict()
        self._set_client()

    @abstractmethod
    def _set_client(self):
        pass

    def get_total_amount(self, query_name: str, exp: str, associations: Flipdict) \
            -> Tuple[int, int, int, int, int, int]:
        self._verbose_output(VerbosityLevel.INFO, f'Getting results amount for {query_name} ...')
        cache = {}
        if self._simulate:
            cache = self._cache.copy()
        translator = SpacesTranslator(associations)
        results = 0
        self._verbose_output(VerbosityLevel.DEBUG, f'Getting total amount of sub-queries for {query_name}...')
        subqueries_total = self.get_sub_queries_amount(exp)
        self._verbose_output(VerbosityLevel.INFO, f'Sub-queries amount for {query_name}: {subqueries_total}')
        time_min, time_max = self._estimated_time(subqueries_total)
        self._verbose_output(VerbosityLevel.INFO,
                             f'Estimated time without caching for {query_name}: from {time_min} to {time_max}')
        subqueries_to_be_done = 0
        performed_subqueries = 0
        negative_non_performed = 0
        positive_non_performed = 0
        for q, sum_factor in self._get_subqueries(exp):
            query = translator.get_translated_query(q)
            results_obtained = True
            if q not in self._cache:
                if not self._simulate:
                    results_obtained, sub_amount = self._issue_query(query)
                else:
                    sub_amount = 0
                    results_obtained = False
                    self._verbose_output(VerbosityLevel.DEBUG, f'Query to issue', query)
                self._cache[q] = sub_amount
                if results_obtained:
                    performed_subqueries += 1
                subqueries_to_be_done += 1
            else:
                self._verbose_output(VerbosityLevel.DEBUG, f'Query already cached', query)
                sub_amount = self._cache[q]
            if results_obtained:
                results += sum_factor * sub_amount
            elif sum_factor > 0:
                positive_non_performed += 1
            else:
                negative_non_performed += 1
        if self._simulate:
            self._cache = cache
        return (results, subqueries_total,
                subqueries_to_be_done, performed_subqueries,
                positive_non_performed, negative_non_performed)

    def _get_subqueries(self, exp: str) -> FrozenSet[str]:
        """This method implements an inclusion-exclusion principle"""
        query_list = exp.split(" | ")
        sum_factor = 1
        for p in range(1, len(query_list) + 1):
            for comb in combinations(query_list, p):
                yield self._get_conjunction_query(comb), sum_factor
            sum_factor *= -1

    @staticmethod
    def _get_conjunction_query(queries: Iterable[str]) -> FrozenSet[str]:
        conjunction_query = frozenset()
        for query in queries:
            if query[0] == '(':
                query = query.strip()[1:-1]
            conjunction_query = conjunction_query | frozenset(query.split(' & '))
        return conjunction_query

    @abstractmethod
    def _issue_query(self, query: str) -> Tuple[bool, int]:
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


class GithubEngine(Engine):
    class SearchType(XEnum):
        CODE = 'code'
        COMMITS = 'commits'
        ISSUES = 'issues'
        REPOSITORIES = 'repositories'
        TOPICS = 'topics'
        USERS = 'users'
        DEFAULT = CODE

    DEFAULTS_DICT = {
        'user': None,
        'passw': None,
        'search_type': SearchType.CODE,
        'url': 'https://api.github.com',
        'retry': 5,
        'timeout': 60,
        'logging': False,
        'waiting_factor': 5
    }

    def __init__(self, simulate: bool,
                 admit_incomplete: bool,
                 user: Optional[str] = None,
                 passw: Optional[str] = None,
                 search_type: Optional[SearchType] = None,
                 url: Optional[str] = None,
                 retry: Optional[Union[int, str]] = None,
                 timeout: Optional[Union[int, str]] = None,
                 logging: Optional[Union[bool, str]] = None,
                 waiting_factor: Optional[Union[int, str]] = None):
        search_type, retry, timeout, logging = cast_tuple_from_str(
            (search_type, retry, timeout, logging),
            (self.SearchType, int, int, bool)
        )
        self._set_attributes(user=user, passw=passw,
                             search_type=search_type,
                             url=url, retry=retry,
                             timeout=timeout,
                             waiting_factor=waiting_factor)
        super().__init__(simulate, admit_incomplete)
        if self._get_value('logging', logging):
            github.enable_console_debug_logging()
        if not self._simulate:
            self.__SEARCH_METHOD = {
                self.SearchType.CODE: self._client.search_code,
                self.SearchType.COMMITS: self._client.search_commits,
                self.SearchType.ISSUES: self._client.search_issues,
                self.SearchType.REPOSITORIES: self._client.search_repositories,
                self.SearchType.TOPICS: self._client.search_topics,
                self.SearchType.USERS: self._client.search_users
            }

    def _set_client(self):
        if not self._simulate:
            try:
                self._verbose_output(VerbosityLevel.INFO, 'Creating client...')
                self._client = Github(login_or_token=self._user,
                                      password=self._passw,
                                      base_url=self._url)
                self._verbose_output(VerbosityLevel.INFO, 'Client created')
                self._verbose_output(VerbosityLevel.INFO, 'Getting rate limit...')
                rate_limit = self._client.get_rate_limit().search.limit
                self._delay = 60 / rate_limit
                self._verbose_output(VerbosityLevel.INFO, f'Rate limit: {rate_limit}')
            except BadCredentialsException as e:
                self._critical_error(f'Authentication failed', ExitCode.AUTHENTICATION, e)
            except ConnectionError as e:
                self._critical_error(f'Connection error', ExitCode.CONNECTION, e)
        else:
            self._delay = 2  # this value is the delay if the user is authenticated

    def _issue_query(self, query: str) -> Tuple[bool, int]:
        delay = get_waiting_time(self._delay, self._waiting_factor)
        self._verbose_output(VerbosityLevel.DEBUG, f'Waiting {delay:.2f} seconds')
        time.sleep(delay)
        for i in range(self._retry):
            try:
                while self._client.get_rate_limit().search.remaining == 0:
                    timeout = get_waiting_time(self._timeout, self._waiting_factor)
                    self._verbose_output(VerbosityLevel.WARNING, f'Rate limit reached. Waiting {timeout:.2f}')
                    time.sleep(timeout)
                self._verbose_output(VerbosityLevel.DEBUG, f'Issuing query', query)
                r = self.__SEARCH_METHOD[self._search_type](query)
                try:
                    _ = r[0]  # <- must be done in order to get the actual totalCount
                except IndexError:
                    pass
                self._verbose_output(VerbosityLevel.DEBUG, f'Results amount: {r.totalCount}')
                return True, r.totalCount
            except RateLimitExceededException as e:
                self._verbose_output(VerbosityLevel.ERROR,
                                     f'Rate limit exceeded', e)
                timeout = get_waiting_time(self._timeout, self._waiting_factor)
                self._verbose_output(VerbosityLevel.WARNING,
                                     f'Waiting {timeout:.2f} seconds...')
                time.sleep(timeout)
            except ConnectionError as e:
                self._verbose_output(VerbosityLevel.ERROR,
                                     f'Connection error', e)
                timeout = get_waiting_time(self._timeout, self._waiting_factor)
                self._verbose_output(VerbosityLevel.WARNING,
                                     f'Waiting {timeout:.2f} seconds...')
                time.sleep(timeout)
                self._set_client()
            except GithubException as e:
                if self._admit_incomplete:
                    self._verbose_output(VerbosityLevel.ERROR, 'Error while issuing query', e)
                    return False, 0
                else:
                    self._critical_error('Error while issuing query', ExitCode.QUERY_ERROR, e)
        if self._admit_incomplete:
            self._verbose_output(VerbosityLevel.ERROR, 'Retry max amount reached')
            return False, 0
        else:
            self._critical_error('Retry max amount reached', ExitCode.QUERY_ERROR)

    def _estimated_time(self, subqueries_total: int) -> Tuple[str, str]:
        return get_time_prognostic(subqueries_total, self._delay, self._waiting_factor)


GithubEngine.__name__ = normalize_name(GithubEngine.__name__)


class EngineType(XEnum):
    GITHUB = 'github'
    DEFAULT = GITHUB


engine_classes = {
    EngineType.GITHUB: GithubEngine
}

__all__ = ['Engine', 'GithubEngine', 'EngineType', 'engine_classes']
