import argparse
from pathlib import Path

from lib.config.consts import APPLICATION_NAME_VERSION, QUERY_NAME_FORMAT, COMMANDLINE_NAME, OUTPUT_FILE_EXT
from lib.internal_logic.caches import CacheType
from lib.internal_logic.engines import EngineType
from lib.internal_logic.parsers import SyntaxType
from lib.utilities.enums import VerbosityLevel
from lib.utilities.functions import get_tuple_caster, get_caster_to_optional


class CustomArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, arg_line):
        return arg_line.split()


def config_args():
    args_parser = CustomArgumentParser(
        description=f"""
                          {APPLICATION_NAME_VERSION}!
     Obtains the results amount of complex queries to Github
                        Use with caution!
    """,
        epilog="""
    Author:
               Ernesto Soto Gómez
                 <esoto@uci.cu>
            <esto.yinyang@gmail.com>
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@'
    )

    args_parser.add_argument('-V', '--version', action='version', version=APPLICATION_NAME_VERSION)

    args_parser.add_argument('queries', metavar='QUERY', type=str, nargs='*', default=[],
                             help='a query or queries to be issue to the server.'
                                  ' The same parser will be used.'
                                  ' This means that the variables in a query will'
                                  ' be used, if specified, in subsequent queries from'
                                  ' the commandline. A result will be shown for each query'
                                  ' in the format'
                                  f' {QUERY_NAME_FORMAT.format(query_namespace=COMMANDLINE_NAME, i="I")}'
                                  ' where I is the position of the query in the commandline')

    # ------------- File managing -------------
    file_managing_group = args_parser.add_argument_group(title='file managing',
                                                         description='options to specify input and output files')

    file_managing_group.add_argument('-i', '--input', nargs='+', action='append',
                                     type=get_caster_to_optional(Path),
                                     default=[],
                                     dest='input_paths',
                                     help='specify input file(s) or directories.'
                                          ' Each file may contain one or many queries.'
                                          ' The same parser will be used for all the specified files.'
                                          ' This means that the variables in a query will'
                                          ' be used, if specified, in subsequent queries from'
                                          ' the same file or other files.'
                                          ' A result will be shown for each query of each file'
                                          ' in the format <filename>.<query_number> where <filename>'
                                          ' is the name (in uppercase) of the file and <query_number>'
                                          ' is the position of the query in the file.'
                                          ' If queries from the commandline are specified,'
                                          ' those queries will be executed first')
    file_managing_group.add_argument('-o', '--output', metavar='PATH', type=get_caster_to_optional(Path),
                                     dest='output_path',
                                     help='specify that each output must be stored in the specified '
                                          'file or a directory if PATH ends with "/". '
                                          'If PATH is a directory then '
                                          'the output will be in one file per query. '
                                          'Each output file will contain the results of each specified query. '
                                          'First files will contain the results of the queries of the '
                                          'commandline if any. The name of the files will be in the format '
                                          f'{QUERY_NAME_FORMAT.format(query_namespace="NAME", i="I")}. '
                                          f'{OUTPUT_FILE_EXT} '
                                          f'where NAME is "{COMMANDLINE_NAME}" or the name of some input file '
                                          'and I is the corresponding query number of the commandline or the '
                                          'referenced input file in "name", respectively.')

    file_managing_group.add_argument('--log-file', metavar=('LEVEL', 'FILE'),
                                     nargs=2, action='append', default=[],
                                     type=get_tuple_caster(VerbosityLevel.cast_from_name, argparse.FileType('w')),
                                     dest='log_files',
                                     help='set files for logging". Each FILE will store '
                                          'information in accordance with the specified LEVEL. '
                                          'LEVEL must be one of the set '
                                          f'{{{VerbosityLevel.sorted_values_string()}}}')

    # ------------- Console output -------------
    console_output_group = args_parser.add_argument_group(title='console output',
                                                          description='options to provide or suppress information about'
                                                                      ' the execution of the program')

    console_output_group.add_argument('--silent', action='store_true',
                                      dest='silent',
                                      help='activate the silent mode.'
                                           ' In this mode, no information about of the results'
                                           ' of the queries is shown in the console.'
                                           ' When this option is not specified, all the information is '
                                           ' printed to the console')

    console_output_group.add_argument('-v', '--verbose', type=get_caster_to_optional(VerbosityLevel.cast_from_name),
                                      choices={None} | set(VerbosityLevel),
                                      default=VerbosityLevel.default(),
                                      dest='verbose',
                                      help='sets the verbosity level.'
                                           ' Once a level is set all the messages'
                                           ' of that kind and those of higher hierarchy'
                                           ' are shown in the standard output or stored'
                                           ' in a file if the --log-file option is specified.'
                                           ' The hierarchy of verbosity levels are as follow,'
                                           ' from higher to lower: '
                                           f'{VerbosityLevel.sorted_values_string() + ", none"}.'
                                           ' The information is showed in the standard output.'
                                           f' (Default: {VerbosityLevel.default()})')

    # ------------- Results -------------
    results_group = args_parser.add_argument_group(title='results',
                                                   description='options that affect the results')

    results_group.add_argument('-s', '--simulate', action='store_true',
                               dest='simulate',
                               help='activate the simulation mode.'
                                    ' In dependence of the complexity of the queries,'
                                    ' this program makes several requests to the server.'
                                    ' In simulation mode no actual request will be issued'
                                    ' to the server')

    results_group.add_argument('-p', '--approximate', action='store_true',
                               dest='admit_incomplete',
                               help='Activate the "approximate" mode. '
                                    'In this mode the sub-queries that can not be '
                                    'done -because of an engine restriction or a'
                                    'problem in the connection- are taken as if '
                                    'they have zero results')

    # ------------- Engines -------------
    engines_group = args_parser.add_argument_group(title='engines',
                                                   description='options to specify or show'
                                                               ' information about the engines')
    engines_group.add_argument('-e', '--engine', choices=EngineType,
                               default=EngineType.default(), type=EngineType.cast_from_name,
                               dest='engine_type',
                               help='sets the engine to use for issuing the queries.'
                                    'If this option is not specified'
                                    f'(Default {EngineType.default()})'
                                    ' (Currently there is only one engine. In the'
                                    ' future another engines may be incorporated)')

    engines_group.add_argument('-E', '--engine-args', metavar=('KEY', 'VALUE'),
                               nargs=2, action='append', default=[],
                               dest='engine_args',
                               help='Set arguments for the engine. '
                                    ' Use --engine-defaults to see the default values'
                                    ' for a given engine')

    engines_group.add_argument('--engine-info', nargs='?', choices=EngineType,
                               const=EngineType.default(), type=EngineType.cast_from_name,
                               dest='engine_info',
                               help='show information about the specified engine.'
                                    f' (Default: {EngineType.default()})')

    engines_group.add_argument('--engine-defaults-info', nargs='?', choices=EngineType,
                               const=EngineType.default(), type=EngineType.cast_from_name,
                               dest='engine_defaults_info',
                               help='Show information about the default values of the Engine'
                                    ' used to issue the queries. If no engine is specified'
                                    ' the default values of the currently selected Engine'
                                    ' will be shown. See -e/--engine option to see how to '
                                    ' set the current engine')

    # ------------- Parsing -------------
    parsing_group = args_parser.add_argument_group(title='parsing',
                                                   description='options to specify or show'
                                                               ' information about the queries syntax')

    parsing_group.add_argument('-x', '--syntax', choices=SyntaxType,
                               default=SyntaxType.default(), type=SyntaxType.cast_from_name,
                               dest='syntax_type',
                               help='sets the syntax to check in the queries.'
                                    f' (Default: {SyntaxType.default()})'
                                    ' (Currently there is only one syntax.'
                                    ' In the future another syntaxes may be'
                                    ' incorporated.)')

    parsing_group.add_argument('-X', '--parser-args', metavar=('KEY', 'VALUE'),
                               nargs=2, action='append', default=[],
                               dest='parser_args',
                               help='Set arguments for the parser. '
                                    ' Use --parser-defaults to see the default values'
                                    ' for a given parser')

    parsing_group.add_argument('--parser-info', nargs='?', choices=SyntaxType,
                               const=SyntaxType.default(), type=SyntaxType.cast_from_name,
                               dest='parser_info',
                               help='show information about the parser used for '
                                    ' the specified syntax'
                                    f' (Default: {SyntaxType.default()})')

    parsing_group.add_argument('--parser-defaults-info', nargs='?', choices=SyntaxType,
                               const=SyntaxType.default(), type=SyntaxType.cast_from_name,
                               dest='parser_defaults_info',
                               help='Show information about the default values of the Parser'
                                    ' used to check the specified syntax. If no syntax is specified'
                                    ' the default values of the Parser for the currently selected'
                                    ' syntax will be shown. See -x/--syntax option to see how to '
                                    ' set the current syntax')

    # ------------- Cache -------------
    cache_group = args_parser.add_argument_group(title='cache',
                                                 description='options to specify or show'
                                                             ' information about the cache')
    cache_group.add_argument('-c', '--cache', choices=CacheType,
                             default=CacheType.default(), type=CacheType.cast_from_name,
                             dest='cache_type',
                             help='sets the cache to be used. '
                                  f'(Default: {CacheType.default()})')

    cache_group.add_argument('-C', '--cache-args', metavar=('KEY', 'VALUE'),
                             nargs=2, action='append', default=[],
                             dest='cache_args',
                             help='Set arguments for the cache. '
                                  ' Use --cache-defaults-info to see the default values'
                                  ' for a given engine')

    cache_group.add_argument('--input-cache', metavar=('TYPE', 'CACHE_NAME'),
                             nargs='+', action='append', default=[],
                             dest='input_caches',
                             help='Copy the content of the specified cache into the current '
                                  'used cache. The specified')

    cache_group.add_argument('--cache-info', nargs='?', choices=CacheType,
                             const=CacheType.default(), type=CacheType.cast_from_name,
                             dest='cache_info',
                             help='show information about the specified cache '
                                  f' (Default: {SyntaxType.default()})')

    cache_group.add_argument('--cache-defaults-info', nargs='?', choices=CacheType,
                             const=CacheType.default(), type=CacheType.cast_from_name,
                             dest='cache_defaults_info',
                             help='Show information about the default values of the specified cache. '
                                  'If no cache is specified the default values of the cache '
                                  'currently selected with -c/--cache option will be shown.')

    # args_parser.print_help()

    return args_parser


# config_args()

__all__ = ['config_args']
