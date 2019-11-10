from io import StringIO
from typing import TextIO, Iterable, Tuple

from lib.config.consts import COMMANDLINE_NAME
from lib.internal_logic.engines import EngineType, engine_classes
from lib.internal_logic.parsers import SyntaxType, parser_classes
from lib.utilities.functions import get_instance


def get_parser(syntax: SyntaxType, parser_args: Iterable[Tuple[str, object]]):
    parser_args = dict(parser_args)
    parser_args.update(query_namespace=COMMANDLINE_NAME)
    return get_instance(parser_classes[syntax], parser_args)


def get_engine(engine: EngineType, simulate: bool, engine_args: Iterable[Tuple[str, object]]):
    engine_args = dict(engine_args)
    engine_args.update(simulate=simulate)
    return get_instance(engine_classes[engine], engine_args)


def run_queries(engine: EngineType, engine_args: Iterable[Tuple[str, object]],
                syntax: SyntaxType, parser_args: Iterable[Tuple[str, object]],
                queries: Iterable[str], input_streams: Iterable[TextIO],
                simulate: bool) -> Tuple[str, int, int, int]:
    engine = get_engine(engine, simulate, engine_args)
    parser = get_parser(syntax, parser_args)

    for code in queries:
        for query_name, exp in parser.get_symbolic_expression(StringIO(code), only_one_query=True):
            yield (query_name, *engine.get_total_amount(query_name, exp, parser.associations))

    for code in input_streams:
        parser.set_namespace(code.name)
        for query_name, exp in parser.get_symbolic_expression(code, only_one_query=False):
            yield (query_name, *engine.get_total_amount(query_name, exp, parser.associations))


__all__ = ['run_queries']
