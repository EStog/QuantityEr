import pprint
from lib.internal_logic.parsers import SyntaxType, parser_classes
from lib.internal_logic.engines import EngineType, engine_classes
from lib.utilities.functions import output


def show_parser_info(syntax: SyntaxType):
    output(f'Description of {parser_classes[syntax].__name__}:\n{parser_classes[syntax].__doc__}')


def show_engine_info(engine: EngineType):
    output(f'Description of {engine_classes[engine].__name__}:\n{engine_classes[engine].__doc__}')


def show_parser_defaults(syntax: SyntaxType):
    output(f'Defaults for {parser_classes[syntax].__name__}:\n'
           f'{pprint.pformat(parser_classes[syntax].DEFAULTS_DICT)}')


def show_engine_defaults(engine: SyntaxType):
    output(f'Defaults for {engine_classes[engine].__name__}:\n'
           f'{pprint.pformat(parser_classes[engine].DEFAULTS_DICT)}')


def show_result(simulate: bool,
                queryname: str,
                results: int,
                subqueries_total: int,
                subqueries_to_be_done: int,
                performed_subqueries: int,
                positive_non_performed: int,
                negative_non_performed: int):
    if not simulate:
        already_cached_subqueries = subqueries_total - subqueries_to_be_done
        already_cached_queries_percent = already_cached_subqueries / subqueries_total \
            if already_cached_subqueries > 0 else 0
        subqueries_to_be_done_percent = subqueries_to_be_done / subqueries_total \
            if subqueries_to_be_done > 0 else 0
        performed_subqueries_amount_percent = performed_subqueries / subqueries_total \
            if subqueries_total > 0 else 0
        non_performed_subqueries = subqueries_total - performed_subqueries
        non_performed_subqueries_percent = subqueries_total / non_performed_subqueries \
            if non_performed_subqueries > 0 else 0
        positive_non_performed_percent = non_performed_subqueries / positive_non_performed \
            if positive_non_performed > 0 else 0
        negative_non_performed_percent = non_performed_subqueries / negative_non_performed \
            if negative_non_performed > 0 else 0
        difference = positive_non_performed - negative_non_performed
        output(
            (f'Results for query {queryname}:'
             f'\n\tResults: {results}'
             f'\n\tSub-queries total: {subqueries_total}'
             f'\n\t\tAlready cached:  {already_cached_subqueries} ({already_cached_queries_percent:.5%})'
             f'\n\t\tTo be performed: {subqueries_to_be_done} ({subqueries_to_be_done_percent:.5%})'
             f'\n\t\t\tPerformed:     {performed_subqueries} ({performed_subqueries_amount_percent:.5%})'
             f'\n\t\t\tNon-performed: {non_performed_subqueries} ({non_performed_subqueries_percent:.5%})'
             f'\n\t\t\t\tTo be added:      {positive_non_performed} ({positive_non_performed_percent:.5%})'
             f'\n\t\t\t\tTo be subtracted: {negative_non_performed} ({negative_non_performed_percent:.5%})'
             f'\n\t\t\t\tDifference:       {difference}').expandtabs(
                4)
        )
    else:
        already_cached_subqueries = subqueries_total - subqueries_to_be_done
        already_cached_queries_percent = already_cached_subqueries / subqueries_total \
            if already_cached_subqueries > 0 else 0
        subqueries_to_be_done_percent = subqueries_to_be_done / subqueries_total \
            if subqueries_to_be_done > 0 else 0
        output(
            (f'Results for query {queryname} in simulation mode:'
             f'\nSub-queries total: {subqueries_total}'
             f'\n\tAlready cached:  {already_cached_subqueries} ({already_cached_queries_percent:.5%})'
             f'\n\tTo be performed: {subqueries_to_be_done} ({subqueries_to_be_done_percent:.5%})').expandtabs(4)
        )
