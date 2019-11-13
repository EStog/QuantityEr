import time
from datetime import datetime
from typing import Tuple

import github
from github import Github, BadCredentialsException, GithubException, Rate
from urllib3 import Retry

from lib.config.consts import QUOTE_FORMAT
from lib.internal_logic.caches.cache import Cache
from lib.internal_logic.engines.engine import Engine
from lib.utilities.classes import Argument
from lib.utilities.enums import VerbosityLevel, ExitCode, XEnum
from lib.utilities.functions import get_waiting_time, get_time_prognostic, normalize_name


class GithubEngine(Engine):
    class SearchType(XEnum):
        CODE = Github.search_code
        COMMITS = Github.search_commits
        ISSUES = Github.search_issues
        REPOSITORIES = Github.search_repositories
        TOPICS = Github.search_topics
        USERS = Github.search_users
        DEFAULT = CODE

    DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

    def _init_parameters(self):
        self._user = Argument(type=str, default=None)
        self._passw = Argument(type=str, default=None)
        self._search_type = Argument(type=self.SearchType.cast_from_name,
                                     default=self.SearchType.DEFAULT)
        self._url = Argument(type=str, default='https://api.github.com')
        self._logging = Argument(type=bool, default=False)
        self._waiting_factor = Argument(type=int, default=5)
        self._total_retry = Argument(type=int, default=10)
        self._connect_retry = Argument(type=int, default=None)
        self._read_retry = Argument(type=int, default=None)
        self._status_retry = Argument(type=int, default=None)
        self._backoff_factor = Argument(type=int, default=6)
        self._backoff_max = Argument(type=int, default=600)

    def __init__(self, cache: Cache, simulate: bool,
                 admit_incomplete: bool, **kwargs):
        super().__init__(cache, simulate, admit_incomplete, **kwargs)
        if self._logging:
            github.enable_console_debug_logging()

    def _set_client(self):
        if not self._simulate:
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
                self._verbose_output(VerbosityLevel.DEBUG, 'Creating client ...')
                self._client = Github(login_or_token=self._user,
                                      password=self._passw,
                                      base_url=self._url,
                                      retry=retry)
                self._verbose_output(VerbosityLevel.DEBUG, 'Client created')
                self._verbose_output(VerbosityLevel.DEBUG, 'Getting rate limit ...')
                limit = self._client.get_rate_limit().search.limit
                self._verbose_output(VerbosityLevel.DEBUG, 'Rate limit per minute', limit)
                self._delay = 60 / limit
                self._verbose_output(VerbosityLevel.DEBUG, 'Delay time', self._delay)
            except BadCredentialsException as e:
                self._critical_error(f'Authentication failed', ExitCode.AUTHENTICATION, e)
            except ConnectionError as e:
                self._critical_error(f'Connection error', ExitCode.CONNECTION, e)
        else:
            self._delay = 6  # this is the delay for unauthenticated users

    def _issue_query(self, name: str, query: str) -> Tuple[bool, int]:
        delay = get_waiting_time(self._delay, self._waiting_factor)
        self._verbose_output(VerbosityLevel.DEBUG, f'Delaying {delay:.2f} seconds')
        time.sleep(delay)
        x = self._client.get_rate_limit().search
        while x.remaining == 0:
            self._verbose_output(VerbosityLevel.DEBUG, 'Rate limit reached')
            delay = self._get_reset_time(x)
            self._verbose_output(VerbosityLevel.DEBUG, f'Waiting {delay.seconds} seconds')
            time.sleep(delay.seconds)
            x = self._client.get_rate_limit().search
        self._verbose_output(VerbosityLevel.DEBUG, f'Issuing subquery {QUOTE_FORMAT.format(name)} ...')
        try:
            r = self._search_type(self._client, query)
            try:
                _ = r[0]  # <- must be done in order to get the actual totalCount
            except IndexError:
                pass
            return True, r.totalCount
        except GithubException as e:
            if e.status == 422 and self._admit_incomplete:
                self._verbose_output(VerbosityLevel.ERROR,
                                     f'Error while issuing subquery {QUOTE_FORMAT.format(name)}', e)
                self._verbose_output(VerbosityLevel.DEBUG,
                                     f'Subquery {QUOTE_FORMAT.format(name)} will be discarded', e)
                return False, 0
            else:
                self._critical_error(f'Error while issuing subquery {QUOTE_FORMAT.format(name)}',
                                     ExitCode.QUERY_ERROR, e)

    def _estimated_time(self, subqueries_total: int) -> Tuple[str, str]:
        return get_time_prognostic(subqueries_total, self._delay, self._waiting_factor)

    def _get_reset_time(self, x: Rate):
        self._verbose_output(VerbosityLevel.DEBUG, f'Getting reset time ...')
        return x.reset - datetime.strptime(x.raw_headers['date'], self.DATE_FORMAT)

    def _get_server_current_datetime(self) -> datetime:
        self._verbose_output(VerbosityLevel.DEBUG, f'Getting server current datetime ...')
        return datetime.strptime(self._client.get_rate_limit().raw_headers['date'], self.DATE_FORMAT)


GithubEngine.__name__ = normalize_name(GithubEngine.__name__)

__all__ = ['GithubEngine']
