import random

import colorama

from lib.config.functions.config_args import config_args
from lib.config.functions.config_loggers import config_loggers
from lib.internal_logic.main import run_queries
from lib.presentation import show_engine_info, show_parser_info, \
    show_engine_defaults, show_parser_defaults, show_result

parser = config_args()

# args = parser.parse_args(['-i', 'query_asyncio.txt', 'query_multiprocessing.txt', '-o',
#                           #                           '-o' 'results_async.txt',
#                           '-v', 'info',
#                           #                           '--log-file', 'debug', './debug_async.txt',
#                           '--simulate'])

args = parser.parse_args()

colorama.init()
random.seed()

config_loggers(args.silent, args.verbose,
               args.log_files)

if args.show_engine_info:
    show_engine_info(args.show_engine_info)

if args.show_engine_defaults_info:
    show_engine_defaults(args.show_engine_defaults_info)

if args.show_parser_info:
    show_parser_info(args.show_parser_info)

if args.show_parser_defaults_info:
    show_parser_defaults(args.show_parser_defaults_info)

for result in run_queries(args.engine_type, args.engine_args,
                          args.syntax_type, args.parser_args,
                          args.queries, args.input_files,
                          args.output_in_files,
                          args.simulate, args.admit_incomplete):
    show_result(args.simulate, *result)
