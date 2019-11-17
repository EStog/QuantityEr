import argparse
import shlex
from abc import ABC, abstractmethod
from typing import Type, Sequence

from lib.consts import AUTHOR


class CustomArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, arg_line):
        return shlex.split(arg_line, comments=True)


class CustomFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass


class WithExternalArguments(ABC):
    """This class manage its defaults in a way that can be presented to the outside"""

    AUTHOR = AUTHOR
    VERSION = '1.0'
    ARG_NAME = ''

    def __init__(self, args_sequence: Sequence = None, prefix_chars='-',
                 fromfile_prefix_chars='@', version_arguments=('-v', '--version'),
                 formatter_class: Type[argparse.HelpFormatter] = CustomFormatter):
        self._args_parser = CustomArgumentParser(
            prog=self.ARG_NAME,
            description=str(self.__doc__),
            epilog=self.AUTHOR,
            formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars
        )
        self._init_arguments()
        self._args_parser.add_argument(*version_arguments,
                                       action='version',
                                       version=f'{self.__class__.__name__} '
                                               f'{self.VERSION}')
        if args_sequence is not None:
            self._args_parser.parse_args(args_sequence, namespace=self)
        else:
            self._args_parser.parse_args(namespace=self)

    @abstractmethod
    def _init_arguments(self):
        """
        Define here the arguments parser using argparse library
        """
        pass
