from lib.config.consts import QUOTE_FORMAT
from lib.utilities.classes import WithDefaults
from lib.utilities.functions import output


def show_object_info(obj: WithDefaults):
    output(f'Description of {obj.__name__}:\n\n{obj.__doc__}')


def show_object_defaults_info(obj: WithDefaults):
    output(f'Defaults for {obj.__name__}:\n\n{obj.get_defaults_info()}')


def show_result(simulate: bool,
                query_name: str,
                results: int,
                subqueries_total: int,
                issued_subqueries: int,
                without_error_subqueries: int,
                with_error_to_be_added: int,
                with_error_to_be_substracted: int):
    if not simulate:
        already_cached_subqueries = subqueries_total - issued_subqueries
        already_cached_queries_percent = already_cached_subqueries / subqueries_total \
            if already_cached_subqueries > 0 else 0
        issued_subqueries_percent = issued_subqueries / subqueries_total \
            if issued_subqueries > 0 else 0
        without_error_subqueries_percent = without_error_subqueries / subqueries_total \
            if subqueries_total > 0 else 0
        with_error_subqueries = subqueries_total - without_error_subqueries
        with_error_subqueries_percent = subqueries_total / with_error_subqueries \
            if with_error_subqueries > 0 else 0
        positive_with_error_percent = with_error_subqueries / with_error_to_be_added \
            if with_error_to_be_added > 0 else 0
        negative_with_error_percent = with_error_subqueries / with_error_to_be_substracted \
            if with_error_to_be_substracted > 0 else 0
        difference = with_error_to_be_added - with_error_to_be_substracted
        output(
            (f'Results for query {QUOTE_FORMAT.format(query_name)}:\n'
             f'\n\tResults: {results}\n'
             f'\n\tSub-queries total: {subqueries_total}'
             f'\n\t\tAlready cached:  {already_cached_subqueries} ({already_cached_queries_percent:.5%})'
             f'\n\t\tIssued:          {issued_subqueries} ({issued_subqueries_percent:.5%})'
             f'\n\t\t\tWithout error: {without_error_subqueries} ({without_error_subqueries_percent:.5%})'
             f'\n\t\t\tWith error:    {with_error_subqueries} ({with_error_subqueries_percent:.5%})'
             f'\n\t\t\t\tTo be added:      {with_error_to_be_added} ({positive_with_error_percent:.5%})'
             f'\n\t\t\t\tTo be subtracted: {with_error_to_be_substracted} ({negative_with_error_percent:.5%})'
             f'\n\t\t\t\tDifference:       {difference}').expandtabs(
                4)
        )
    else:
        already_cached_subqueries = subqueries_total - issued_subqueries
        already_cached_queries_percent = already_cached_subqueries / subqueries_total \
            if already_cached_subqueries > 0 else 0
        issued_subqueries_percent = issued_subqueries / subqueries_total \
            if issued_subqueries > 0 else 0
        output(
            (f'Results for query {QUOTE_FORMAT.format(query_name)} in simulation mode:\n'
             f'\n\tResults: {results}\n'
             f'\nSub-queries total: {subqueries_total}'
             f'\n\tAlready cached: {already_cached_subqueries} ({already_cached_queries_percent:.5%})'
             f'\n\tIssued:         {issued_subqueries} ({issued_subqueries_percent:.5%})').expandtabs(4)
        )
