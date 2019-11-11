import time
from abc import abstractmethod
from datetime import datetime
from itertools import combinations
from typing import Iterable, Tuple, Set

import github
from github import Github, RateLimitExceededException, \
    BadCredentialsException, GithubException
from requests import ConnectionError
from urllib3.util.retry import Retry

from lib.config.consts import SUBQUERY_NAME_FORMAT, QUOTE_FORMAT
from lib.internal_logic.caches import Cache
from lib.internal_logic.translators import SpacesTranslator
from lib.utilities.classes import WithDefaults, Firm
from lib.utilities.enums import XEnum, VerbosityLevel, ExitCode
from lib.utilities.flip_dict import Flipdict
from lib.utilities.functions import normalize_name, \
    get_waiting_time, get_included_excluded_principle_iter_amount, get_time_prognostic


class Engine(WithDefaults):

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

    def get_total_amount(self, query_name: str, exp: str, associations: Flipdict) \
            -> Tuple[int, int, int, int, int, int]:
        self._verbose_output(VerbosityLevel.DEBUG,
                             f'Getting results amount for query {QUOTE_FORMAT.format(query_name)} ...')
        backup_cache = {}
        if self._simulate:
            backup_cache = self._cache.copy()
        translator = SpacesTranslator()
        results = 0
        self._verbose_output(VerbosityLevel.DEBUG,
                             f'Getting total amount of subqueries for {QUOTE_FORMAT.format(query_name)}...')
        subqueries_total = self.get_sub_queries_amount(exp)
        self._verbose_output(VerbosityLevel.INFO, f'Subqueries amount for {QUOTE_FORMAT.format(query_name)}',
                             subqueries_total)
        if not self._simulate:
            time_min, time_max = self._estimated_time(subqueries_total)
            self._verbose_output(VerbosityLevel.INFO,
                                 f'Estimated time without caching for query {QUOTE_FORMAT.format(query_name)}',
                                 f'from {time_min} to {time_max}')
        issued_subqueries = 0
        without_error_subqueries = 0
        with_error_to_be_substracted = 0
        with_error_to_be_added = 0
        i = 0
        init = datetime.now()
        for query, sum_factor in self._get_subqueries(exp):
            query = translator.get_particular_query(query, associations)
            i += 1
            subquery_name = SUBQUERY_NAME_FORMAT.format(query_name=query_name, i=i)
            self._verbose_output(VerbosityLevel.DEBUG,
                                 f'Subquery {QUOTE_FORMAT.format(subquery_name)} of {subqueries_total}', query)
            if query not in self._cache:
                self._verbose_output(VerbosityLevel.DEBUG, f'Subquery {QUOTE_FORMAT.format(subquery_name)} to issue')
                if not self._simulate:
                    no_error, sub_amount = self._issue_query(subquery_name, query)
                else:
                    sub_amount = 0
                    no_error = True
                if no_error:
                    self._cache[query] = sub_amount
                    self._verbose_output(VerbosityLevel.DEBUG,
                                         f'Results amount cached for subquery {QUOTE_FORMAT.format(subquery_name)}')
                    without_error_subqueries += 1
                else:
                    if sum_factor > 0:
                        with_error_to_be_added += 1
                    else:
                        with_error_to_be_substracted += 1
                issued_subqueries += 1
            else:
                self._verbose_output(VerbosityLevel.DEBUG,
                                     f'Results amount for subquery {QUOTE_FORMAT.format(subquery_name)} already cached')
                sub_amount = self._cache[query]
            self._verbose_output(VerbosityLevel.DEBUG,
                                 f'Results amount for subquery {QUOTE_FORMAT.format(subquery_name)}', sub_amount)
            results += sum_factor * sub_amount

        end = datetime.now()
        self._verbose_output(VerbosityLevel.INFO, f'Runtime for query {QUOTE_FORMAT.format(query_name)}', end - init)
        if self._simulate:
            self._cache = backup_cache
        return (results, subqueries_total,
                issued_subqueries, without_error_subqueries,
                with_error_to_be_added, with_error_to_be_substracted)

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


class SearchType(XEnum):
    CODE = Github.search_code
    COMMITS = Github.search_commits
    ISSUES = Github.search_issues
    REPOSITORIES = Github.search_repositories
    TOPICS = Github.search_topics
    USERS = Github.search_users
    DEFAULT = CODE


class GithubEngine(Engine):
    class _KW(XEnum):
        USER = Firm(ttype=str, default=None)
        PASSW = Firm(ttype=str, default=None)
        SEARCH_TYPE = Firm(ttype=SearchType.cast_from_name, default=SearchType.DEFAULT)
        URL = Firm(ttype=str, default='https://api.github.com')
        LOGGING = Firm(ttype=bool, default=False)
        WAITING_FACTOR = Firm(ttype=int, default=5)
        TOTAL_RETRY = Firm(ttype=int, default=10)
        CONNECT_RETRY = Firm(ttype=int, default=None)
        READ_RETRY = Firm(ttype=int, default=None)
        STATUS_RETRY = Firm(ttype=int, default=None)
        BACKOFF_FACTOR = Firm(ttype=int, default=5)
        BACKOFF_MAX = Firm(ttype=int, default=300)

    def __init__(self, cache: Cache, simulate: bool,
                 admit_incomplete: bool, **kwargs):
        super().__init__(cache, simulate, admit_incomplete, **kwargs)
        if self._get(self._KW.LOGGING):
            github.enable_console_debug_logging()

    def _set_client(self):
        if not self._simulate:
            try:
                retry = Retry(total=self._get(self._KW.TOTAL_RETRY),
                              connect=self._get(self._KW.CONNECT_RETRY),
                              read=self._get(self._KW.READ_RETRY),
                              redirect=False,
                              status=self._get(self._KW.STATUS_RETRY),
                              status_forcelist=[403],
                              backoff_factor=self._get(self._KW.BACKOFF_FACTOR),
                              raise_on_status=True,
                              respect_retry_after_header=True)
                retry.RETRY_AFTER_STATUS_CODES = retry.RETRY_AFTER_STATUS_CODES | {403}
                retry.BACKOFF_MAX = self._get(self._KW.BACKOFF_MAX)
                self._verbose_output(VerbosityLevel.DEBUG, 'Creating client...')
                self._client = Github(login_or_token=self._get(self._KW.USER),
                                      password=self._get(self._KW.PASSW),
                                      base_url=self._get(self._KW.URL),
                                      retry=retry)
                self._verbose_output(VerbosityLevel.DEBUG, 'Client created')
                limit = self._client.get_rate_limit().search.limit
                self._verbose_output(VerbosityLevel.DEBUG, 'Rate limit per minute', limit)
                self._delay = 60/limit
                self._verbose_output(VerbosityLevel.DEBUG, 'Delay time', self._delay)
            except BadCredentialsException as e:
                self._critical_error(f'Authentication failed', ExitCode.AUTHENTICATION, e)
            except ConnectionError as e:
                self._critical_error(f'Connection error', ExitCode.CONNECTION, e)

    def _issue_query(self, name: str, query: str) -> Tuple[bool, int]:
        search_type = self._get(self._KW.SEARCH_TYPE)
        delay = get_waiting_time(self._delay, self._get(self._KW.WAITING_FACTOR))
        self._verbose_output(VerbosityLevel.DEBUG, f'Delaying {delay:.2f} seconds')
        time.sleep(delay)
        x = self._client.get_rate_limit().search
        while x.remaining == 0:
            self._verbose_output(VerbosityLevel.DEBUG, 'Rate limit reached')
            delay = x.reset - datetime.strptime(x.raw_headers['date'], '%a, %d %b %Y %H:%M:%S %Z')
            self._verbose_output(VerbosityLevel.DEBUG, f'Waiting {delay.seconds} seconds')
            time.sleep(delay.seconds)
            x = self._client.get_rate_limit().search
            self._verbose_output(VerbosityLevel.DEBUG, f'Issuing subquery {QUOTE_FORMAT.format(name)}...')
        try:
            r = search_type(self._client, query)
            try:
                _ = r[0]  # <- must be done in order to get the actual totalCount
            except IndexError:
                pass
        except GithubException as e:
            if e.data == 422 and self._admit_incomplete:
                self._verbose_output(VerbosityLevel.ERROR,
                                     f'Error while issuing subquery {QUOTE_FORMAT.format(name)}', e)
                self._verbose_output(VerbosityLevel.DEBUG,
                                     f'Subquery {QUOTE_FORMAT.format(name)} will be discarded', e)
                return False, 0
            else:
                self._critical_error(f'Error while issuing subquery {QUOTE_FORMAT.format(name)}',
                                     ExitCode.QUERY_ERROR, e)
        else:
            return True, r.totalCount
        if self._admit_incomplete:
            self._verbose_output(VerbosityLevel.DEBUG,
                                 f'Retry max amount reached for subquery {QUOTE_FORMAT.format(name)}')
            self._verbose_output(VerbosityLevel.DEBUG, f'Query {QUOTE_FORMAT.format(name)} will be discarded')
            return False, 0
        else:
            self._critical_error(f'Retry max amount reached for query {QUOTE_FORMAT.format(name)}',
                                 ExitCode.QUERY_ERROR)

    def _estimated_time(self, subqueries_total: int) -> Tuple[str, str]:
        return get_time_prognostic(subqueries_total, self._delay, self._get(self._KW.WAITING_FACTOR))


GithubEngine.__name__ = normalize_name(GithubEngine.__name__)


class EngineType(XEnum):
    GITHUB = GithubEngine
    DEFAULT = GITHUB


__all__ = ['Engine', 'EngineType']
