import logging
from io import StringIO
from typing import TextIO, Iterable, Tuple, Union

from lib.config.consts import COMMANDLINE_NAME, OUTPUT_LOGGER_NAME, FILE_OUTPUT_FORMAT, \
    OUTPUT_FILE_EXT
from lib.internal_logic.engines import EngineType, engine_classes, Engine
from lib.internal_logic.parsers import SyntaxType, parser_classes, Parser
from lib.utilities.enums import ExitCode, VerbosityLevel
from lib.utilities.functions import get_instance, critical_error, verbose_output


def get_parser(syntax: SyntaxType, parser_args: Iterable[Tuple[str, object]]):
    parser_args = dict(parser_args)
    parser_args.update(query_namespace=COMMANDLINE_NAME)
    return get_instance(parser_classes[syntax], parser_args)


def get_engine(engine: EngineType, simulate: bool, admit_incomplete: bool,
               engine_args: Iterable[Tuple[str, object]]):
    engine_args = dict(engine_args)
    engine_args.update(simulate=simulate)
    engine_args.update(admit_incomplete=admit_incomplete)
    return get_instance(engine_classes[engine], engine_args)


def __run_queries(engine: Engine, parser: Parser,
                  queries: Union[Iterable[str], Iterable[TextIO]],
                  output_in_files: bool, console: bool):
    output_logger = logging.getLogger(OUTPUT_LOGGER_NAME)
    file_formatter = logging.Formatter(
        FILE_OUTPUT_FORMAT,
        style='{')
    for code in queries:
        if console:
            code = StringIO(code)
        else:
            parser.set_namespace(code.name)
        for query_name, exp in parser.get_symbolic_expression(code, only_one_query=console):
            if output_in_files:
                filename = f'{query_name}.{OUTPUT_FILE_EXT}'
                try:
                    file = open(filename, 'w')
                except OSError as e:
                    critical_error(f'Cannot open file {filename} for output', ExitCode.FILE_ERROR, error=e)
                else:
                    handler = logging.StreamHandler(file)
                    handler.setFormatter(file_formatter)
                    output_logger.addHandler(handler)
                    results = engine.get_total_amount(query_name, exp, parser.associations)
                    yield (query_name, *results)
                    output_logger.removeHandler(handler)
                    file.close()


def run_queries(engine: EngineType, engine_args: Iterable[Tuple[str, object]],
                syntax: SyntaxType, parser_args: Iterable[Tuple[str, object]],
                queries: Iterable[str],
                input_streams: Iterable[TextIO],
                output_in_files: bool,
                simulate: bool, admit_incomplete: bool) -> Tuple[str, int, int, int, int, int, int]:
    engine = get_engine(engine, simulate, admit_incomplete, engine_args)
    parser = get_parser(syntax, parser_args)

    if simulate:
        verbose_output(VerbosityLevel.WARNING,
                       'Simulation activated. Will not execute any actual query')
    elif admit_incomplete:
        verbose_output(VerbosityLevel.WARNING,
                       'Approximate mode activated. Will continue in case of critical error')

    for r in __run_queries(engine, parser, queries, output_in_files, console=True):
        yield r
    for r in __run_queries(engine, parser, input_streams, output_in_files, console=False):
        yield r


__all__ = ['run_queries']
