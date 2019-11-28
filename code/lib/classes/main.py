import argparse
import logging
from pathlib import Path
from typing import Iterable, Sequence

import colorama

from lib.classes.inputs.file_input import FileInput
from lib.classes.inputs.input import Input
from lib.classes.inputs.str_input import StrInput
from lib.classes.internal.caches import DEFAULT_CACHE_TYPE, CACHE_TYPE, \
    INPUT_CACHE_TYPE
from lib.classes.internal.engines import ENGINE_TYPE, DEFAULT_ENGINE_TYPE
from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.classes.internal.parsers import DEFAULT_PARSER_TYPE, PARSER_TYPE
from lib.classes.outputs.output import Output
from lib.classes.outputs.stream_outputs.console_output import ConsoleOutput
from lib.classes.outputs.stream_outputs.file_output import FileOutput
from lib.utilities.functions import get_caster_to_optional, get_tuple_caster, \
    get_members_set_string, get_component
from lib.utilities.logging import VerbosityLevel
from lib.utilities.logging.consts import VERBOSITY_LOGGER_NAME, CONSOLE_OUTPUT_FORMAT, FILE_OUTPUT_FORMAT
from lib.utilities.logging.with_logging import WithLogging
from lib.utilities.with_external_arguments import WithExternalArguments


class Main(WithLogging, WithExternalArguments):

    def __init__(self, args_sequence: Sequence[str] = None):
        WithLogging.__init__(self)
        WithExternalArguments.__init__(self, args_sequence)

    def run(self):
        self._prologue()
        self._main_logic()
        self._epilogue()

    def _prologue(self):
        colorama.init()
        self._config_loggers()

    def _get_inputs(self) -> Iterable[Input]:
        # noinspection PyUnresolvedReferences
        if not self.queries and self.input_paths is None:
            self._args_parser.error('No input specified')
        inputs = []
        # noinspection PyUnresolvedReferences
        if self.queries:
            # noinspection PyUnresolvedReferences
            inputs.append(StrInput(self.queries,
                                   self.parser_options,
                                   self._args_parser))
        # noinspection PyUnresolvedReferences
        if self.input_paths is not None:
            # noinspection PyUnresolvedReferences
            for ll in self.input_paths:
                if not ll:
                    # noinspection PyUnresolvedReferences
                    inputs.append(FileInput(Path('./'),
                                            self.parser_options,
                                            self._args_parser))
                else:
                    for path in ll:
                        # noinspection PyUnresolvedReferences
                        inputs.append(FileInput(path,
                                                self.parser_options,
                                                self._args_parser))
        return inputs

    def _get_outputs(self) -> Iterable[Output]:
        # noinspection PyUnresolvedReferences
        if self.silent and not self.output_paths:
            self._args_parser.error('No output specified')
        outputs = []
        # noinspection PyUnresolvedReferences
        if not self.silent:
            outputs.append(ConsoleOutput())
        # noinspection PyUnresolvedReferences
        if self.output_paths:
            # noinspection PyUnresolvedReferences
            for ll in self.output_paths:
                if not ll:
                    outputs.append(FileOutput(None))
                else:
                    for path in ll:
                        outputs.append(FileOutput(path))
        return outputs

    def _main_logic(self):
        inputs = self._get_inputs()
        outputs = self._get_outputs()
        # noinspection PyUnresolvedReferences
        engine = get_component(self.engine_options, ENGINE_TYPE, 'engine',
                               self._args_parser,
                               cache_options=self.cache_options,
                               input_caches_options=self.input_caches_options,
                               simulate=self.simulate,
                               main_args_parser=self._args_parser)
        for i in inputs:
            for middle_code in i.get_middle_codes():
                results = engine.get_total_amount(middle_code)
                for output in outputs:
                    # noinspection PyUnresolvedReferences
                    output.output(middle_code, self.simulate, results)

    def _epilogue(self):
        pass

    def _config_loggers(self):
        verbosity_logger = logging.getLogger(VERBOSITY_LOGGER_NAME)
        verbosity_logger.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            CONSOLE_OUTPUT_FORMAT,
            style='{')
        file_formatter = logging.Formatter(
            FILE_OUTPUT_FORMAT,
            style='{')
        verbosity_logger.addHandler(logging.NullHandler())
        # noinspection PyUnresolvedReferences
        if self.console_verbose:
            console_verbosity_handler = logging.StreamHandler()
            # noinspection PyUnresolvedReferences
            console_verbosity_handler.setLevel(self.console_verbose.value)
            console_verbosity_handler.setFormatter(console_formatter)
            verbosity_logger.addHandler(console_verbosity_handler)
        # noinspection PyUnresolvedReferences
        if self.log_files:
            # noinspection PyUnresolvedReferences
            for e in self.log_files:
                if len(e) % 2 != 0:
                    self._args_parser.error(f'Arguments amount to --log-files must be even')
                while len(e) > 0:
                    verbosity_level, file, e = e[0], e[1], e[2:]
                    handler = logging.StreamHandler(file)
                    handler.setFormatter(file_formatter)
                    handler.setLevel(verbosity_level.value)
                    verbosity_logger.addHandler(handler)

    def _init_arguments(self):
        self._args_parser.add_argument('queries', metavar='QUERY', type=str, nargs='*',
                                       help='a query or queries to be issue to the server. '
                                            'The same parser will be used for all the queries '
                                            'in the same program run. '
                                            'This means the variables in a query will '
                                            'be used, if specified, in subsequent queries. '
                                            'Each query will be named as '
                                            f'''{MiddleCode.MIDDLE_CODE_NAME_FORMAT.format(
                                                namespace=StrInput.COMMANDLINE_NAME, name="I")} '''
                                            'where I is a sequential number associated to the query '
                                            'when it is  processed')

        # ------------- File managing -------------
        file_managing_group = self._args_parser.add_argument_group(title='file managing',
                                                                   description='options to specify '
                                                                               'inputs and outputs files')

        file_managing_group.add_argument('-i', '--inputs', dest='input_paths',
                                         nargs='*', metavar='PATH', action='append',
                                         type=Path,
                                         help='specify inputs file(s) or directories.'
                                              'Each file may contain one or many queries separated by spaces. '
                                              'If the path is an existing directory, then all the files with '
                                              f'extension {FileInput.INPUT_FILE_EXT} will be considered input '
                                              f'files. If PATH is not specified the current working directory '
                                              f'will be used.'
                                              'The same parser will be used for all the queries '
                                              'in the same program run. '
                                              'This means the variables in a query will '
                                              'be used, if specified, in subsequent queries. ')
        file_managing_group.add_argument('-o', '--outputs', dest='output_paths', nargs='*',
                                         metavar='PATH', type=Path, action='append',
                                         help='specify that each output must be stored in the specified '
                                              'file or directory. If PATH is a directory then '
                                              'the outputs will be in one file per query. '
                                              'The name of the files will be in the format '
                                              f'{FileOutput.OUTPUT_FILE_FORMAT} '
                                              f'or ({FileOutput.OUTPUT_SIMULATION_FILE_FORMAT} '
                                              f'when in simulation mode) where "name" is the name '
                                              f'of the corresponding query. '
                                              f'If PATH is not specified the output files will be'
                                              f'stored in te same directories of the inputs. If the '
                                              f'inputs are from the console, the output files will be '
                                              f'stored in an "{StrInput.COMMANDLINE_NAME}" directory in'
                                              f'the current working directory. '
                                              'This option may be specified several times')

        file_managing_group.add_argument('--log-files', dest='log_files',
                                         metavar=('LEVEL', 'FILE'),
                                         nargs='+', action='append',
                                         type=get_tuple_caster(VerbosityLevel.cast_from_name, argparse.FileType('w')),
                                         help='set of files for logging". Each FILE will store '
                                              'information in accordance with the specified LEVEL. '
                                              'LEVEL must be one of the set '
                                              f'{{{VerbosityLevel.sorted_names_string()}}}. '
                                              f'The amount of arguments to this option must be even. '
                                              f'This option may be specified several times.')

        # ------------- Console outputs -------------
        console_output_group = self._args_parser.add_argument_group(title='console outputs',
                                                                    description='options to provide or suppress '
                                                                                'information about the execution '
                                                                                'of the program')

        console_output_group.add_argument('--silent', action='store_true', dest='silent',
                                          help='activate the silent mode. '
                                               'In this mode, no information about of the results '
                                               'of the queries is shown in the console. '
                                               'When this option is not specified, all the information '
                                               'output is printed to the console ')

        console_output_group.add_argument('-V', '--verbose', dest='console_verbose', nargs='?',
                                          type=get_caster_to_optional(VerbosityLevel.cast_from_name),
                                          choices=VerbosityLevel,
                                          const=VerbosityLevel.default(),
                                          help='sets the verbosity level. '
                                               'Once a level is set all the messages '
                                               'of that kind and those of higher hierarchy '
                                               'are shown in the standard outputs or stored '
                                               'in a file if the --log-file option is specified. '
                                               'The hierarchy of verbosity levels are as follow, '
                                               'from higher to lower: '
                                               f'{VerbosityLevel.sorted_names_string()}. '
                                               'The information is showed in the standard outputs.')

        # ------------- Results -------------
        results_group = self._args_parser.add_argument_group(title='results',
                                                             description='options that affect the results')

        results_group.add_argument('-s', '--simulate', action='store_true',
                                   dest='simulate',
                                   help='activate the simulation mode. '
                                        ' In dependence of the complexity of the queries, '
                                        ' this program makes several requests to the server. '
                                        ' In simulation mode no actual request will be issued '
                                        ' to the server')

        # ------------- Engines -------------
        engines_group = self._args_parser.add_argument_group(title='engines',
                                                             description='options to specify or show'
                                                                         ' information about the engines')
        engines_group.add_argument('-e', '--engine', dest='engine_options', nargs='+',
                                   metavar=(f'{get_members_set_string(ENGINE_TYPE)}', 'ARGS'),
                                   # type=get_component_caster(ENGINE_TYPE, 'engine type'),
                                   default=DEFAULT_ENGINE_TYPE,
                                   help='sets the engine to use for issuing the queries. '
                                        '(Currently there is only one engine. In the '
                                        'future another engines may be incorporated) ')

        # ------------- Parsing -------------
        parsing_group = self._args_parser.add_argument_group(title='parsing',
                                                             description='options to specify or show'
                                                                         ' information about the queries syntax')

        parsing_group.add_argument('-p', '--parser', dest='parser_options',
                                   metavar=(f'{get_members_set_string(PARSER_TYPE)}', 'ARGS'),
                                   # type=get_component_caster(PARSER_TYPE, 'parser type'),
                                   default=DEFAULT_PARSER_TYPE, nargs='+',
                                   help='sets the parser to use for checking the syntax of the queries. '
                                        ' (Currently there is only one parser. '
                                        ' In the future another parsers may be '
                                        ' incorporated.)')

        # ------------- Cache -------------
        cache_group = self._args_parser.add_argument_group(title='cache',
                                                           description='options to specify or show'
                                                                       ' information about the cache')
        cache_group.add_argument('-c', '--cache', dest='cache_options', nargs='+',
                                 metavar=(f'{get_members_set_string(CACHE_TYPE)}', 'ARGS'),
                                 # type=get_component_caster(CACHE_TYPE, 'cache type'),
                                 default=DEFAULT_CACHE_TYPE,
                                 help='sets the cache to be used.')

        cache_group.add_argument('--input-cache', dest='input_caches_options', nargs=2, action='append',
                                 metavar=(f'{get_members_set_string(INPUT_CACHE_TYPE)}', 'FILENAME'),
                                 # type=get_component_caster(INPUT_CACHE_TYPE, 'input cache type'),
                                 default=[],
                                 help='Copy the content of the specified cache into the current '
                                      'used cache. This argument may be specified several times.')
