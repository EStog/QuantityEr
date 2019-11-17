from abc import abstractmethod
from datetime import datetime
from typing import TextIO

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.classes.outputs.output import Output
from lib.utilities.functions import div, quote


class StreamOutput(Output):

    def __init__(self, tab_size=4):
        Output.__init__(self)
        self._tab_size = tab_size

    def _get_message(self, middle_code: MiddleCode, is_simulation: bool,
                     results: int, subqueries_total: int, issued_subqueries: int,
                     without_error_subqueries: int, with_error_to_be_added: int,
                     with_error_to_be_subtracted: int, estimated_time_min: datetime,
                     estimated_time_max: datetime, estimated_time_caching_min: datetime,
                     estimated_time_caching_max: datetime, begin_run_datetime: datetime,
                     end_run_datetime: datetime, longest_subquery: str) -> str:

        delimiter = '--------------------------------------------------------------------'

        message = (f'\n\n{delimiter}\n'
                   f'\tResults for query {middle_code.name} from '
                   f'{quote(middle_code.namespace)}{{simulation_message}}\n'
                   f'\n\t\tResults amount: {results}\n'
                   f'\n\t\tSub-queries total: {subqueries_total}\n')

        already_cached_subqueries = subqueries_total - issued_subqueries
        if already_cached_subqueries:
            already_cached_queries_percent = div(already_cached_subqueries, subqueries_total) * 100
            message += (
                f'\t\t\tFrom cache:      {already_cached_subqueries} '
                f'({already_cached_queries_percent:g}% of total)\n')

        if issued_subqueries:
            issued_subqueries_percent = div(issued_subqueries, subqueries_total) * 100
            message += (
                f'\t\t\t{{issue}}{issued_subqueries} '
                f'({issued_subqueries_percent:g}% of total)\n')

        if without_error_subqueries and without_error_subqueries != issued_subqueries:
            without_error_subqueries_percent = div(without_error_subqueries, issued_subqueries) * 100
            message += (
                f'\t\t\t\tWithout error: {without_error_subqueries} '
                f'({without_error_subqueries_percent:g}% of issued)\n')

        with_error_subqueries = issued_subqueries - without_error_subqueries
        with_error_subqueries_percent = div(with_error_subqueries, issued_subqueries) * 100
        if with_error_subqueries:
            message += (
                f'\t\t\t\tWith error:    {with_error_subqueries} '
                f'({with_error_subqueries_percent:g}% of issued)\n')

        with_error_to_be_added_percent = div(with_error_to_be_added, with_error_subqueries) * 100
        if with_error_to_be_added:
            message += (
                f'\t\t\t\t\tTo be added:      {with_error_to_be_added} '
                f'({with_error_to_be_added_percent:g}% of with error)\n')

        with_error_to_be_subtracted_percent = div(with_error_to_be_subtracted, with_error_subqueries) * 100
        if with_error_to_be_subtracted:
            message += (
                f'\t\t\t\t\tTo be subtracted: {with_error_to_be_subtracted} '
                f'({with_error_to_be_subtracted_percent:g}% of with error)\n')

        difference = with_error_to_be_added - with_error_to_be_subtracted
        if difference:
            message += f'\t\\tt\t\tDifference:       {difference}\n'

        message += (f'\n\t\t{{location}} begin datetime: {begin_run_datetime}\n'
                    f'\t\t{{location}} end datetime:   {end_run_datetime}\n'

                    f'\n\t\tRuntime:                           {end_run_datetime - begin_run_datetime}'
                    f'\n\t\tEstimated runtime with caching:    '
                    f'from {estimated_time_caching_min} to {estimated_time_caching_max}'
                    f'\n\t\tEstimated runtime without caching: '
                    f'from {estimated_time_min} to {estimated_time_max}')

        if is_simulation:
            message = message.format(
                simulation_message=(f' in simulation mode:\n'
                                    '\t(Results are from the cache)'),
                issue=f'To be issued:{" " * 4}',
                location='Local')
        else:
            message = message.format(
                simulation_message='',
                issue=f'Issued:{" " * 10}',
                location='Server'
            )

        message += f'\n\n\n\tThe processed query was:\n\n{middle_code.original_query}'
        message += f'\n\n\n\tLongest subquery:\n\n{longest_subquery}'
        message += f'\n\n\n\tLongest Subquery atoms quantity:      {len(longest_subquery.split(" "))}'
        message += f'\n\tLongest Subquery characters quantity: {len(longest_subquery)}'

        message += f'\n{delimiter}\n\n'

        return message

    @abstractmethod
    def _get_stream(self, middle_code: MiddleCode, is_simulation: bool) -> TextIO:
        pass

    def output(self, middle_code: MiddleCode, is_simulation: bool, results):
        self._get_stream(middle_code, is_simulation).write(
            self._get_message(middle_code, is_simulation, *results).expandtabs(self._tab_size))
