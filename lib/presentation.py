import datetime

from lib.config.consts import QUOTE_FORMAT
from lib.utilities.classes import WithArguments
from lib.utilities.functions import output, div


def show_object_info(obj: WithArguments):
    output(f'Description of {obj.__name__}:\n\n{obj.__doc__}')


def show_object_defaults_info(obj: WithArguments):
    output(f'Defaults for {obj.__name__}:\n\n{obj.get_defaults_info()}')


def show_result(simulate: bool,
                query_name: str,
                results: int,
                subqueries_total: int,
                issued_subqueries: int,
                without_error_subqueries: int,
                with_error_to_be_added: int,
                with_error_to_be_substracted: int,
                estimated_time_min: datetime,
                estimated_time_max: datetime,
                begin_run_datetime: datetime,
                end_run_datetime: datetime):
    already_cached_subqueries = subqueries_total - issued_subqueries
    already_cached_queries_percent = div(already_cached_subqueries, subqueries_total) * 100
    issued_subqueries_percent = div(issued_subqueries, subqueries_total) * 100

    message = (
        '{head}'
        f'\n\t\tResults amount: {results}\n'
        f'\n\t\tSub-queries total: {subqueries_total}\n').expandtabs(4)
    if already_cached_subqueries:
        message += (
            f'\t\t\tAlready cached:  {already_cached_subqueries} '
            f'({already_cached_queries_percent:g}% of total)\n').expandtabs(4)
    if issued_subqueries:
        message += (
            f'\t\t\t{{issue}}{issued_subqueries} '
            f'({issued_subqueries_percent:g}% of total)\n').expandtabs(4)

    with_error_subqueries = issued_subqueries - without_error_subqueries
    difference = with_error_to_be_added - with_error_to_be_substracted

    without_error_subqueries_percent = div(without_error_subqueries, subqueries_total) * 100
    without_error_subqueries_percent1 = div(without_error_subqueries, issued_subqueries) * 100
    with_error_subqueries_percent = div(with_error_subqueries, subqueries_total) * 100
    with_error_subqueries_percent1 = div(with_error_subqueries, issued_subqueries) * 100
    with_error_to_be_added_percent = div(with_error_to_be_added, subqueries_total) * 100
    with_error_to_be_added_percent1 = div(with_error_to_be_added, with_error_subqueries) * 100
    with_error_to_be_substracted_percent = div(with_error_to_be_substracted, subqueries_total) * 100
    with_error_to_be_substracted_percent1 = div(with_error_to_be_substracted, with_error_subqueries) * 100

    if without_error_subqueries:
        message += (
            f'\t\t\t\tWithout error: {without_error_subqueries} '
            f'({without_error_subqueries_percent:g}% of total, '
            f'{without_error_subqueries_percent1:g}% of issued)\n').expandtabs(4)
    if with_error_subqueries:
        message += (
            f'\t\t\t\tWith error:    {with_error_subqueries} '
            f'({with_error_subqueries_percent:g}% of total, '
            f'{with_error_subqueries_percent1:g}% of issued)\n').expandtabs(4)
    if with_error_to_be_added:
        message += (
            f'\t\t\t\t\tTo be added:      {with_error_to_be_added} '
            f'({with_error_to_be_added_percent:g}% of total, '
            f'{with_error_to_be_added_percent1:g}% of with error)\n').expandtabs(4)
    if with_error_to_be_substracted:
        message += (
            f'\t\t\t\t\tTo be subtracted: {with_error_to_be_substracted} '
            f'({with_error_to_be_substracted_percent:g}% of total, '
            f'{with_error_to_be_substracted_percent1:g}% of with error)\n').expandtabs(4)
    if difference:
        message += f'\t\\tt\t\tDifference:       {difference}\n'.expandtabs(4)

    message += (f'\n\t\t{{location}} begin datetime: {begin_run_datetime}\n'
                f'\t\t{{location}} end datetime:   {end_run_datetime}\n'

                f'\n\t\tRuntime:                           {end_run_datetime - begin_run_datetime}'
                f'\n\t\tEstimated runtime without caching: '
                f'from {estimated_time_min} to {estimated_time_max}\n\n').expandtabs(4)

    if simulate:
        output(
            message.format(
                head=(f'\n\tResults for query {QUOTE_FORMAT.format(query_name)} in simulation mode:'
                      '\n\t(Results are from the cache)\n'),
                issue=f'To be issued:{" " * 4}',
                location='Local')
        )
    else:
        output(
            message.format(
                head=f'\n\tResults for query {QUOTE_FORMAT.format(query_name)}:\n',
                issue=f'Issued:{" " * 10}',
                location='Server'
            )
        )
