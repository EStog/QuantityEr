import random

import colorama

from lib.config.functions.config_args import config_args
from lib.config.functions.config_loggers import config_loggers
from lib.internal_logic.main import run_queries, update_cache
from lib.presentation import show_result, show_object_info, show_object_defaults_info

parser = config_args()

# args = parser.parse_args(['-i', 'query_asyncio.txt', 'query_multiprocessing.txt', '-o',
#                           '-v', 'debug', '--log-file', 'debug', 'debug.log',
#                           '--log-file', 'info', 'info.log'])

args = parser.parse_args()

colorama.init()
random.seed()

config_loggers(args.silent, args.verbose,
               args.log_files)

if args.engine_info:
    show_object_info(args.engine_info.value)

if args.engine_defaults_info:
    show_object_defaults_info(args.engine_defaults_info.value)

if args.parser_info:
    show_object_info(args.parser_info.value)

if args.parser_defaults_info:
    show_object_defaults_info(args.parser_defaults_info.value)

if args.cache_info:
    show_object_info(args.cache_info.value)

if args.cache_defaults_info:
    show_object_defaults_info(args.cache_defaults_info.value)

cache = args.cache_type.value(**dict(args.cache_args))

if args.input_caches:
    update_cache(cache, args.input_caches)

if not args.queries and not args.input_files:
    exit(0)  # if the is no queries to process, exit silently.
engine = args.engine_type.value(cache, args.simulate, args.admit_incomplete, **dict(args.engine_args))
parser = args.syntax_type.value(**dict(args.parser_args))

for result in run_queries(engine, parser,
                          args.queries, args.input_files,
                          args.output_in_files,
                          args.simulate, args.admit_incomplete):
    show_result(args.simulate, *result)