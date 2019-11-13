import random

import colorama

from lib.config.functions.config_args import config_args
from lib.config.functions.config_loggers import config_loggers
from lib.internal_logic.main import run_queries, get_cache
from lib.presentation import show_result, show_object_info, show_object_defaults_info

parser = config_args()

# args = parser.parse_args(['-i', './testing/', '-i', './query-multiprocessing.txt', '-o', './testing', '-s'])

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

for result in run_queries(args.engine_type, args.engine_args,
                          args.syntax_type, args.parser_args,
                          get_cache(args.cache_type, args.cache_args, args.input_caches),
                          args.queries, args.input_paths,
                          args.output_path,
                          args.simulate, args.admit_incomplete):
    show_result(args.simulate, *result)
