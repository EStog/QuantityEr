import logging
from io import StringIO
from typing import TextIO, Iterable, Tuple, Union

from lib.config.consts import OUTPUT_LOGGER_NAME, FILE_OUTPUT_FORMAT, \
    OUTPUT_FILE_EXT
from lib.internal_logic.caches import Cache, InputCacheType
from lib.internal_logic.engines import Engine
from lib.internal_logic.parsers import Parser
from lib.utilities.enums import ExitCode, VerbosityLevel
from lib.utilities.functions import critical_error, verbose_output


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
            parser.set_namespace(code.name.replace('../', '..').replace('./', '.').replace('/', '.'))
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


def run_queries(engine: Engine, parser: Parser,
                queries: Iterable[str], input_streams: Iterable[TextIO],
                output_in_files: bool,
                simulate: bool, admit_incomplete: bool) -> Tuple[str, int, int, int, int, int, int]:
    if simulate:
        verbose_output(VerbosityLevel.WARNING,
                       'Simulation activated. Will not execute any actual query')
    elif admit_incomplete:
        verbose_output(VerbosityLevel.WARNING,
                       'Approximate mode activated. Will continue in case of validation error from server')

    for r in __run_queries(engine, parser, queries, output_in_files, console=True):
        yield r
    for r in __run_queries(engine, parser, input_streams, output_in_files, console=False):
        yield r


def update_cache(cache: Cache, input_caches: Iterable[Tuple[str, ...]]):
    for input_cache_type, *input_cache_args in input_caches:
        try:
            input_cache_type = InputCacheType.cast_from_name(input_cache_type)
        except TypeError as e:
            critical_error(str(e), ExitCode.TYPING)
        if len(input_cache_args) % 2 != 0:
            critical_error(f'Arguments list for cache input must be of even size', ExitCode.TYPING)
        kwargs = {}
        while input_cache_args:
            key, value, *input_cache_args = input_cache_args
            kwargs[key] = value
        input_cache = input_cache_type.value(**kwargs)
        cache.update(input_cache)
        input_cache.close()


__all__ = ['run_queries', 'update_cache']
