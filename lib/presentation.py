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
        with_error_subqueries = issued_subqueries - without_error_subqueries
        difference = with_error_to_be_added - with_error_to_be_substracted

        already_cached_queries_percent = (already_cached_subqueries / subqueries_total
                                          if subqueries_total > 0 else 0)
        issued_subqueries_percent = (issued_subqueries / subqueries_total
                                     if subqueries_total > 0 else 0)
        without_error_subqueries_percent = (without_error_subqueries / subqueries_total
                                            if subqueries_total > 0 else 0)
        without_error_subqueries_percent1 = (without_error_subqueries / issued_subqueries
                                             if issued_subqueries > 0 else 0)
        with_error_subqueries_percent = (with_error_subqueries / subqueries_total
                                         if subqueries_total > 0 else 0)
        with_error_subqueries_percent1 = (with_error_subqueries / issued_subqueries
                                          if issued_subqueries > 0 else 0)
        with_error_to_be_added_percent = (with_error_to_be_added / subqueries_total
                                          if subqueries_total > 0 else 0)
        with_error_to_be_added_percent1 = (with_error_to_be_added / with_error_subqueries
                                           if with_error_subqueries > 0 else 0)
        with_error_to_be_substracted_percent = (with_error_to_be_substracted / subqueries_total
                                                if subqueries_total > 0 else 0)
        with_error_to_be_substracted_percent1 = (with_error_to_be_substracted / with_error_subqueries
                                                 if with_error_subqueries > 0 else 0)

        output(
            (f'Results for query {QUOTE_FORMAT.format(query_name)}:\n'

             f'\n\tResults: {results}\n'

             f'\n\tSub-queries total: {subqueries_total}\n'

             f'\n\t\tAlready cached:  {already_cached_subqueries} '
             f'({already_cached_queries_percent:.5%} of total)'
             f'\n\t\tIssued:          {issued_subqueries} '
             f'({issued_subqueries_percent:.5%} of total)'

             f'\n\t\t\tWithout error: {without_error_subqueries} '
             f'({without_error_subqueries_percent:.5%} of total, '
             f'{without_error_subqueries_percent1:.5%} of issued)'
             f'\n\t\t\tWith error:    {with_error_subqueries} '
             f'({with_error_subqueries_percent:.5%} of total, '
             f'{with_error_subqueries_percent1:.5%} of issued)\n'

             f'\n\t\t\t\tTo be added:      {with_error_to_be_added} '
             f'({with_error_to_be_added_percent:.5%} of total, '
             f'{with_error_to_be_added_percent1:.5%} of with error)'
             f'\n\t\t\t\tTo be subtracted: {with_error_to_be_substracted} '
             f'({with_error_to_be_substracted_percent:.5%} of total, '
             f'{with_error_to_be_substracted_percent1:.5%} of with error)'
             f'\n\t\t\t\tDifference:       {difference}\n').expandtabs(4)
        )
    else:
        already_cached_subqueries = subqueries_total - issued_subqueries
        already_cached_queries_percent = (already_cached_subqueries / subqueries_total
                                          if subqueries_total > 0 else 0)
        issued_subqueries_percent = (issued_subqueries / subqueries_total
                                     if subqueries_total > 0 else 0)
        output(
            (f'Results for query {QUOTE_FORMAT.format(query_name)} in simulation mode:\n'
             f'\n\tResults: {results}\n'
             
             f'\nSub-queries total: {subqueries_total}\n'
             
             f'\n\tAlready cached: {already_cached_subqueries} ({already_cached_queries_percent:.5%})'
             f'\n\tTo be issued:   {issued_subqueries} ({issued_subqueries_percent:.5%})\n').expandtabs(4)
        )
