import logging
import re
from io import StringIO, TextIOBase
from pathlib import Path
from typing import TextIO, Iterable, Tuple, Union, Optional

from lib.config.consts import OUTPUT_LOGGER_NAME, FILE_OUTPUT_FORMAT, INPUT_FILE_EXT, \
    OUTPUT_FILE_FORMAT, OUTPUT_SIMULATION_FILE_FORMAT
from lib.internal_logic.caches import InputCacheType, CacheType
from lib.internal_logic.caches.cache import Cache
from lib.internal_logic.engines import EngineType
from lib.internal_logic.engines.engine import Engine
from lib.internal_logic.parsers import SyntaxType
from lib.internal_logic.parsers.parser import Parser
from lib.utilities.enums import ExitCode, VerbosityLevel
from lib.utilities.functions import critical_error, verbose_output, create_path, open_file


def __run_queries(engine: Engine, parser: Parser,
                  queries: Union[Iterable[str], Iterable[TextIO]],
                  output_path: Optional[Path], console: bool, simulation: bool):
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
            if isinstance(output_path, Path):
                name = query_name.replace('./', '.').replace('/', '.')
                if simulation:
                    filename = OUTPUT_SIMULATION_FILE_FORMAT.format(name=name)
                else:
                    filename = OUTPUT_FILE_FORMAT.format(name=name)
                filename = output_path.joinpath(filename)
                file = open_file(filename, 'w')
                handler = logging.StreamHandler(file)
                handler.setFormatter(file_formatter)
                output_logger.addHandler(handler)
                results = engine.get_total_amount(query_name, exp, parser.symbols_table)
                yield (query_name, *results)
                output_logger.removeHandler(handler)
                file.close()
            else:
                results = engine.get_total_amount(query_name, exp, parser.symbols_table)
                yield (query_name, *results)


def __set_output_path(output_path: Path) -> Union[Path, TextIO]:
    output_logger = logging.getLogger(OUTPUT_LOGGER_NAME)
    file_formatter = logging.Formatter(
        FILE_OUTPUT_FORMAT,
        style='{')
    if output_path:
        if create_path(output_path):
            output_path = open_file(output_path, 'a')
            handler = logging.StreamHandler(output_path)
            handler.setFormatter(file_formatter)
            output_logger.addHandler(handler)
    return output_path


def run_queries(engine_type: EngineType,
                engine_args: Iterable[Tuple[str, str]],
                syntax_type: SyntaxType,
                parser_args: Iterable[Tuple[str, str]],
                cache: Cache,
                queries: Iterable[str],
                input_paths: Iterable[Path],
                output_path: Optional[Path],
                simulate: bool, admit_incomplete: bool) -> Tuple[str, int, int, int, int, int, int]:
    if not queries and not input_paths:
        exit(0)  # if the is no queries to process, exit silently.
    engine = engine_type.value(cache, simulate, admit_incomplete, **dict(engine_args))
    parser = syntax_type.value(**dict(parser_args))

    if simulate:
        verbose_output(VerbosityLevel.WARNING,
                       'Simulation activated. Will not execute any actual query')
    elif admit_incomplete:
        verbose_output(VerbosityLevel.WARNING,
                       'Approximate mode activated. Will continue in case of error in query')

    output_path = __set_output_path(output_path)

    for r in __run_queries(engine, parser, queries, output_path, console=True, simulation=simulate):
        yield r
    for l in input_paths:
        for path in l:
            if path.is_file():
                input_streams = [open_file(path, 'r')]
            elif path.is_dir():
                input_streams = []
                for element in path.iterdir():
                    if re.fullmatch(rf'^.*\.{INPUT_FILE_EXT}$', str(element)):
                        input_streams.append(open_file(element, 'r'))
            else:
                critical_error(f'Path does not exists', ExitCode.FILE_ERROR, Path)
            for r in __run_queries(engine, parser, input_streams, output_path, console=False, simulation=simulate):
                yield r

    if isinstance(output_path, TextIOBase):
        output_path.close()


def get_cache(cache_type: CacheType, cache_args: Iterable[Tuple[str, str]], input_caches: Iterable[Tuple[str, ...]]):
    cache = cache_type.value(**dict(cache_args))
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
    return cache


__all__ = ['run_queries', 'get_cache']
