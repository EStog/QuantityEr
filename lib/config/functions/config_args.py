import argparse

from lib.config.consts import APPLICATION_NAME_VERSION, QUERY_NAME_FORMAT, COMMANDLINE_NAME
from lib.internal_logic.engines import EngineType
from lib.internal_logic.parsers import SyntaxType
from lib.utilities.enums import VerbosityLevel
from lib.utilities.functions import get_verbosity_file_caster, cast_to_verbosity_level_or_none


def config_args():
    args_parser = argparse.ArgumentParser(
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
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    args_parser.add_argument('-V', '--version', action='version', version=APPLICATION_NAME_VERSION)

    args_parser.add_argument('queries', metavar='QUERY', type=str, nargs='*', default=[],
                             help='a query or queries to be issue to the server.'
                                  ' The same parser will be used.'
                                  ' This means that the variables in a query will'
                                  ' be used, if specified, in subsequent queries from'
                                  ' the commandline. A result will be shown for each query'
                                  ' in the format'
                                  f' {QUERY_NAME_FORMAT.format(query_namespace=COMMANDLINE_NAME, n="n")}'
                                  ' where "n" is the position'
                                  ' of the query in the commandline')

    # ------------- File managing -------------
    file_managing_group = args_parser.add_argument_group(title='file managing',
                                                         description='options to specify input and output files')

    file_managing_group.add_argument('-i', '--input', type=argparse.FileType('r'),
                                     action='append', default=[],
                                     dest='input_files',
                                     help='input file(s).'
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
    file_managing_group.add_argument('-o', '--output', type=argparse.FileType('w'),
                                     action='append', default=[],
                                     dest='output_files',
                                     help='output file(s).'
                                          ' Each output file will contain the results of each specified query.'
                                          ' First files will contain the results of the queries of the'
                                          ' commandline if any. If there is less output files than input files,'
                                          ' the extra information will be printed to the standard output')

    file_managing_group.add_argument('--log-file', metavar=('LEVEL', 'FILE'),
                                     nargs=2, action='append', default=[],
                                     type=get_verbosity_file_caster(),
                                     dest='log_files',
                                     help='set files for logging". Each FILE will store'
                                          ' information in accordance with the specified LEVEL.'
                                          ' LEVEL must be one of the set '
                                          f' {{{VerbosityLevel.sorted_values_string()}}}')

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

    console_output_group.add_argument('-v', '--verbose', type=cast_to_verbosity_level_or_none,
                                      choices={None} | set(VerbosityLevel),
                                      default=VerbosityLevel.DEFAULT.value,
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
                                           f' (Default: {VerbosityLevel.DEFAULT.value})')

    # ------------- Testing -------------
    testing_group = args_parser.add_argument_group(title='testing',
                                                   description='options to specify testing settings')

    testing_group.add_argument('-s', '--simulate', action='store_true',
                               dest='simulate',
                               help='activate the simulation mode.'
                                    ' In dependence of the complexity of the queries,'
                                    ' this program makes several requests to the server.'
                                    ' In simulation mode no actual request will be issued'
                                    ' to the server')

    # ------------- Engines -------------
    engines_group = args_parser.add_argument_group(title='engines',
                                                   description='options to specify or show'
                                                               ' information about the engines')
    engines_group.add_argument('-e', '--engine', choices=EngineType,
                               default=EngineType.DEFAULT.value, type=EngineType,
                               dest='engine_type',
                               help='sets the engine to use for issuing the queries.'
                                    'If this option is not specified'
                                    f'(Default {EngineType.DEFAULT.value})'
                                    ' (Currently there is only one engine. In the'
                                    ' future another engines may be incorporated)')

    engines_group.add_argument('-A', '--engine-args', metavar=('KEY', 'VALUE'),
                               nargs=2, action='append', default=[],
                               dest='engine_args',
                               help='Set arguments for the engine. '
                                    ' Use --engine-defaults to see the default values'
                                    ' for a given engine')

    engines_group.add_argument('--engine-info', nargs='?', choices=EngineType,
                               const=EngineType.DEFAULT.value, type=EngineType,
                               dest='show_engine_info',
                               help='show information about the specified engine.'
                                    f' (Default: {EngineType.DEFAULT.value})')

    engines_group.add_argument('--engine-defaults-info', nargs='?', choices=EngineType,
                               const=EngineType.DEFAULT.value, type=EngineType,
                               dest='show_engine_defaults_info',
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
                               default=SyntaxType.DEFAULT.value, type=SyntaxType,
                               dest='syntax_type',
                               help='sets the syntax to check in the queries.'
                                    f' (Default: {SyntaxType.DEFAULT.value})'
                                    ' (Currently there is only one syntax.'
                                    ' In the future another syntaxes may be'
                                    ' incorporated.)')

    parsing_group.add_argument('--parser-info', nargs='?', choices=SyntaxType,
                               const=SyntaxType.DEFAULT.value, type=SyntaxType,
                               dest='show_parser_info',
                               help='show information about parser used for '
                                    ' the specified syntax.'
                                    f' (Default: {SyntaxType.DEFAULT.value})')

    parsing_group.add_argument('-a', '--parser-args', metavar=('KEY', 'VALUE'),
                               nargs=2, action='append', default=[],
                               dest='parser_args',
                               help='Set arguments for the parser. '
                                    ' Use --parser-defaults to see the default values'
                                    ' for a given parser. (This option is only for future'
                                    ' parser additions, and should not be used for the current'
                                    ' version of the program, because there is currently only one'
                                    ' parser and it does not takes any argument)')

    parsing_group.add_argument('--parser-defaults-info', nargs='?', choices=SyntaxType,
                               const=SyntaxType.DEFAULT.value, type=SyntaxType,
                               dest='show_parser_defaults_info',
                               help='Show information about the default values of the Parser'
                                    ' used to check the specified syntax. If no syntax is specified'
                                    ' the default values of the Parser for the currently selected'
                                    ' syntax will be shown. See -x/--syntax option to see how to '
                                    ' set the current syntax')

    # args_parser.print_help()

    return args_parser


# config_args()

__all__ = ['config_args']
