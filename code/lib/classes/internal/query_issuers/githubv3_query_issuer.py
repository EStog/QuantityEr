import random
import time
from datetime import datetime, timedelta
from typing import Tuple

from github import Github, BadCredentialsException, GithubException, Rate
from urllib3 import Retry

from lib.classes.internal.query_issuers.query_issuer import QueryIssuer
from lib.utilities.logging import ExitCode


class GithubV3QueryIssuer(QueryIssuer):
    SEARCH_TYPE = {
        'code': Github.search_code,
        'commits': Github.search_commits,
        'issues': Github.search_issues,
        'repositories': Github.search_repositories,
        'topics': Github.search_topics,
        'users': Github.search_users,
    }
    DEFAULT_SEARCH_TYPE = 'code'

    @classmethod
    def cast_to_search_type(cls, search_type: str):
        return cls.SEARCH_TYPE[search_type]

    __DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

    def __init__(self, user: str, passw: str, url: str,
                 search_type: SEARCH_TYPE, query_max_length: int,
                 admit_long_query: bool,
                 total_retry: int, connect_retry: int,
                 read_retry: int, status_retry: int,
                 backoff_factor: float, backoff_max: int,
                 waiting_factor: int, connect: bool):
        self._user = user
        self._passw = passw
        self._url = url
        self._search_type = search_type
        self._query_max_length = query_max_length
        self._admit_long_query = admit_long_query
        self._total_retry = total_retry
        self._connect_retry = connect_retry
        self._read_retry = read_retry
        self._status_retry = status_retry
        self._backoff_factor = backoff_factor
        self._backoff_max = backoff_max
        self._waiting_factor = waiting_factor
        self._connect = connect
        QueryIssuer.__init__(self)

    def _set_client(self):
        if self._connect:
            try:
                retry = Retry(total=self._total_retry,
                              connect=self._connect_retry,
                              read=self._read_retry,
                              redirect=False,
                              status=self._status_retry,
                              status_forcelist=[403],
                              backoff_factor=self._backoff_factor,
                              raise_on_status=False,
                              respect_retry_after_header=True)
                retry.RETRY_AFTER_STATUS_CODES = retry.RETRY_AFTER_STATUS_CODES | {403}
                retry.BACKOFF_MAX = self._backoff_max
                self._debug('Creating client ...')
                self._client = Github(login_or_token=self._user,
                                      password=self._passw,
                                      base_url=self._url,
                                      retry=retry)
                self._debug('Client created')
                self._debug('Getting rate limit ...')
                limit = self._client.get_rate_limit().search.limit
                self._debug('Rate limit per minute', limit)
                self._delay = 60 / limit
                self._debug('Delay time', self._delay)
            except BadCredentialsException as e:
                self._authentication_critical(e)
            except ConnectionError as e:
                self._connection_critical(e)
        else:
            self._delay = 6  # take the delay as if it is not authenticated

    def issue(self, name: str, query: str) -> Tuple[bool, int]:
        def verbose(func, message, arg=None):
            func(message, arg, header=name)

        verbose(self._debug, f'Getting results amount ...')
        if not self.check_query_length(len(query), name):
            verbose(self._debug, f'Subquery discarded')
            return False, 0
        delay = self._get_waiting_time()
        verbose(self._debug, f'Delaying {delay:.2f} seconds ...')
        time.sleep(delay)
        x = self._client.get_rate_limit().search
        while x.remaining == 0:
            verbose(self._debug, 'Rate limit reached')
            delay = self._get_reset_time(x, name)
            verbose(self._debug, f'Waiting {delay.seconds} seconds ...')
            time.sleep(delay.seconds)
            x = self._client.get_rate_limit().search
        verbose(self._debug, f'Issuing ...')
        try:
            r = self._search_type(self._client, query)
            try:
                _ = r[0]  # <- must be done in order to get the actual totalCount
            except IndexError:
                pass
            return True, r.totalCount
        except GithubException as e:
            verbose(self._query_critical, f'Error while issuing', e)

    def check_query_length(self, query_length: int, name: str) -> bool:
        if query_length > self._query_max_length:
            if self._admit_long_query:
                self._warning(f'Maximum allowed length of {self._query_max_length} exceeded. Subquery length',
                              arg=query_length, header=name)
                return False
            else:
                self._query_critical(f'Maximum allowed length of {self._query_max_length} exceeded. Subquery length',
                                     arg=query_length, header=name)
        else:
            return True

    def get_estimated_time(self, subqueries_total: int) -> Tuple[str, str]:
        return (str(timedelta(seconds=subqueries_total * self._delay)),
                str(timedelta(seconds=subqueries_total * self._delay * self._waiting_factor)))

    def get_server_current_datetime(self) -> datetime:
        self._debug(f'Getting server current datetime ...')
        return datetime.strptime(self._client.get_rate_limit().raw_headers['date'], self.__DATE_FORMAT)

    def _get_waiting_time(self):
        return random.triangular(self._delay, self._delay * self._waiting_factor, self._delay)

    def _get_reset_time(self, x: Rate, name: str):
        self._debug(f'Getting reset time ...', header=name)
        return x.reset - datetime.strptime(x.raw_headers['date'], self.__DATE_FORMAT)

    def _connection_critical(self, error):
        self._critical(f'Connection error', ExitCode.CONNECTION, error)

    def _authentication_critical(self, error):
        self._critical(f'Authentication failed', ExitCode.AUTHENTICATION, error)

    def _query_critical(self, message: str, arg=None, header=None):
        self._critical(message, ExitCode.QUERY_ERROR, arg, header)
