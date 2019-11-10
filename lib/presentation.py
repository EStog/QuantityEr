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
                results_amount: int,
                subqueries_total_amount: int,
                performed_subqueries_amount: int):
    if not simulate:
        output(
            f'Results for query {queryname}:'
            f'\n\tResults amount: {results_amount}'
            f'\n\tSub-queries total amount: {subqueries_total_amount}'
            f'\n\tActually performed sub-queries amount: {performed_subqueries_amount}'
        )
    else:
        output(
            f'Results for query {queryname} in simulation mode:'
            f'\n\tSub-queries total amount: {subqueries_total_amount}'
            f'\n\tActually performed sub-queries amount: {performed_subqueries_amount}'
        )
