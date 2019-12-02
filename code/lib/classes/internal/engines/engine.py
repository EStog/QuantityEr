import random
from abc import ABC
from datetime import datetime
from typing import Tuple, Sequence

from lib.classes import WithLoggingAndExternalArguments
from lib.classes.internal.caches import CACHE_TYPE, INPUT_CACHE_TYPE
from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.functions import get_component
from lib.utilities.with_external_arguments import CustomArgumentParser


class Engine(WithLoggingAndExternalArguments, ABC):

    def __init__(self, args_sequence: Sequence[str],
                 cache_options: Sequence[str],
                 input_caches_options: Sequence[str],
                 simulate: bool,
                 main_args_parser: CustomArgumentParser):
        WithLoggingAndExternalArguments.__init__(self, args_sequence)
        self._simulate = simulate
        self._simulation_cache = set()
        self._decomposer = None
        self._translator = None
        self._query_issuer = None
        self._cache_options = cache_options
        self._input_caches_options = input_caches_options
        self._cache = None
        self._main_args_parser = main_args_parser
        self._set_cache()
        if simulate:
            self._get_amount = self._run_simulation

    def _init_arguments(self):
        self._args_parser.add_argument('**reset-cache', action='store_true')

    def _set_cache(self):
        self._cache = get_component(self._cache_options, CACHE_TYPE, 'cache',
                                    self._main_args_parser)
        for options in self._input_caches_options:
            input_cache = get_component(options, INPUT_CACHE_TYPE, 'input cache',
                                        self._main_args_parser, as_input_cache=True)
            self._cache.update(input_cache)

    def _reset_cache(self):
        self._cache.reset()
        self._simulation_cache = set()
        self._set_cache()

    def get_total_amount(self, middle_code: MiddleCode) -> Tuple[int, int, int,
                                                                 int, int, int,
                                                                 datetime, datetime,
                                                                 datetime, datetime,
                                                                 datetime, datetime,
                                                                 str]:
        random.seed()
        # noinspection PyUnresolvedReferences
        if self.reset_cache:
            self._reset_cache()
        self._decomposer.set_middle_code(middle_code)
        self._debug('Getting results amount ...', header=middle_code.full_name)
        longest_subquery = self._translator.get_particular_query(self._decomposer.longest_subexpression())
        self._debug('Longest subquery', longest_subquery, header=middle_code.full_name)
        longest_subquery_length = len(longest_subquery)
        self._debug('Longest subquery length', longest_subquery_length, header=middle_code.full_name)
        if not self._query_issuer.check_query_restrictions(longest_subquery, middle_code.full_name):
            self._debug('Subqueries that exceeds the maximum allowed length, will be discarded',
                        header=middle_code.full_name)
        self._debug('Getting total amount of subqueries ...', header=middle_code.full_name)
        subqueries_total = self._decomposer.get_sub_queries_amount()
        self._info('Subqueries amount', subqueries_total, header=middle_code.full_name)

        estimated_time_min, estimated_time_max = self._query_issuer.get_estimated_time(subqueries_total)
        self._info('Estimated time without caching',
                   f'from {estimated_time_min} to {estimated_time_max}',
                   header=middle_code.full_name)

        (issued_subqueries, without_error_subqueries,
         with_error_to_be_added, with_error_to_be_subtracted,
         results, begin_run_datetime, end_run_datetime) = self._get_amount(subqueries_total,
                                                                           middle_code)

        (estimated_time_caching_min,
         estimated_time_caching_max) = self._query_issuer.get_estimated_time(issued_subqueries)

        return (results, subqueries_total,
                issued_subqueries, without_error_subqueries,
                with_error_to_be_added, with_error_to_be_subtracted,
                estimated_time_min, estimated_time_max,
                estimated_time_caching_min, estimated_time_caching_max,
                begin_run_datetime, end_run_datetime, longest_subquery)

    def _get_amount(self, subqueries_total, middle_code) -> Tuple[int, int, int, int, int,
                                                                  datetime, datetime]:
        issued_subqueries = 0
        without_error_subqueries = 0
        with_error_to_be_subtracted = 0
        with_error_to_be_added = 0
        results = 0

        begin_run_datetime = self._query_issuer.get_server_current_datetime()
        self._info('Server begin time', begin_run_datetime, header=middle_code.full_name)

        for q, sum_factor in self._decomposer.get_subqueries():
            subquery = self._translator.get_particular_query(q)
            self._debug(f'{q.name} of {subqueries_total}', header=q.full_name, arg=subquery)
            if subquery not in self._cache:
                no_error, sub_amount = self._query_issuer.issue(q.full_name, subquery)
                issued_subqueries += 1
                if no_error:
                    self._cache[subquery] = sub_amount
                    self._debug('Results amount cached', header=q.full_name)
                    self._debug('Results amount', sub_amount, header=q.full_name)
                    without_error_subqueries += 1
                else:
                    if sum_factor > 0:
                        with_error_to_be_added += 1
                    else:
                        with_error_to_be_subtracted += 1
            else:
                sub_amount = self._cache[subquery]
                self._debug(f'Results amount already cached', header=q.full_name)
                self._debug('Results amount', sub_amount, header=q.full_name)
            results += sum_factor * sub_amount

        end_run_datetime = self._query_issuer.get_server_current_datetime()
        self._info('Server end time', end_run_datetime, header=middle_code.full_name)

        return (issued_subqueries, without_error_subqueries,
                with_error_to_be_added, with_error_to_be_subtracted,
                results, begin_run_datetime, end_run_datetime)

    def _run_simulation(self, subqueries_total, middle_code) -> Tuple[int, int, int, int, int,
                                                                      datetime, datetime]:
        to_issue_subqueries = 0
        without_error_subqueries = 0
        results = 0

        begin_run_datetime = datetime.now()
        self._info('Local begin time', begin_run_datetime, header=middle_code.full_name)

        for q, sum_factor in self._decomposer.get_subqueries():
            subquery = self._translator.get_particular_query(q)
            self._debug(f'... of {subqueries_total}', header=q.full_name, arg=subquery)
            sub_amount = 0
            if subquery not in self._simulation_cache:
                if subquery not in self._cache:
                    self._debug('To issue', header=q.full_name)
                    to_issue_subqueries += 1
                    if not self._query_issuer.check_query_restrictions(subquery, q.full_name):
                        self._debug(f'Subquery discarded', header=q.full_name)
                    else:
                        self._simulation_cache.add(subquery)
                        self._debug('Query cached', header=q.full_name)
                        without_error_subqueries += 1
                else:
                    sub_amount = self._cache[subquery]
                    self._debug(f'Results amount already cached', header=q.full_name)
                    self._debug('Results amount', sub_amount, header=q.full_name)
            else:
                self._debug(f'Query already cached', header=q.full_name)
            results += sum_factor * sub_amount

        end_run_datetime = datetime.now()
        self._info('Local end time', end_run_datetime, header=middle_code.full_name)

        return (to_issue_subqueries, without_error_subqueries, 0, 0,
                results, begin_run_datetime, end_run_datetime)
