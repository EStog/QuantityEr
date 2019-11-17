from typing import Sequence

import github

from lib.classes.internal.decomposers.exclusion_inclusion_decomposer import ExclusionInclusionDecomposer
from lib.classes.internal.engines.engine import Engine
from lib.classes.internal.query_issuers.githubv3_query_issuer import GithubV3QueryIssuer
from lib.classes.internal.translators.spaces_translator import SpacesTranslator
from lib.utilities.with_external_arguments import CustomArgumentParser


class GithubV3Engine(Engine):
    ARG_NAME = 'github'

    def _init_arguments(self):
        Engine._init_arguments(self)
        self._args_parser.add_argument('**user')
        self._args_parser.add_argument('**passw')
        self._args_parser.add_argument('**search-type',
                                       default=GithubV3QueryIssuer.DEFAULT_SEARCH_TYPE,
                                       choices=GithubV3QueryIssuer.SEARCH_TYPE.keys(),
                                       type=GithubV3QueryIssuer.cast_to_search_type)
        self._args_parser.add_argument('**url', default='https://api.github.com')
        self._args_parser.add_argument('**logging', action='store_true')
        self._args_parser.add_argument('**admit-long-query', action='store_true')
        self._args_parser.add_argument('**query-max-length', type=int, default=128)
        self._args_parser.add_argument('**waiting-factor', type=int, default=7)
        self._args_parser.add_argument('**total-retry', type=int, default=10)
        self._args_parser.add_argument('**connect-retry', type=int)
        self._args_parser.add_argument('**read-retry', type=int)
        self._args_parser.add_argument('**status-retry', type=int)
        self._args_parser.add_argument('**backoff-factor', type=float, default=6)
        self._args_parser.add_argument('**backoff-max', type=int, default=600)
        self._args_parser.add_argument('**deep-simplify', action='store_true')

    def __init__(self, args_sequence: Sequence[str],
                 cache_options: Sequence[str],
                 input_caches_options: Sequence[str],
                 simulate: bool,
                 main_args_parser: CustomArgumentParser
                 ):
        Engine.__init__(self, args_sequence, cache_options,
                        input_caches_options, simulate,
                        main_args_parser)
        # noinspection PyUnresolvedReferences
        self._decomposer = ExclusionInclusionDecomposer(self.deep_simplify)
        self._translator = SpacesTranslator()
        # noinspection PyUnresolvedReferences
        self._query_issuer = GithubV3QueryIssuer(self.user, self.passw, self.url, self.search_type,
                                                 self.query_max_length, self.admit_long_query,
                                                 self.total_retry, self.connect_retry, self.read_retry,
                                                 self.status_retry, self.backoff_factor, self.backoff_max,
                                                 self.waiting_factor, not simulate)
        # noinspection PyUnresolvedReferences
        if self.logging:
            github.enable_console_debug_logging()
