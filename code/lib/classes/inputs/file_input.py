import re
from pathlib import Path
from typing import Iterable, Sequence

from lib.classes.inputs.input import Input
from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.utilities.file_dir_manager import FileDirManager
from lib.utilities.with_external_arguments import CustomArgumentParser


class FileInput(Input, FileDirManager):
    INPUT_FILE_EXT = 'in'
    input_file_re = re.compile(rf'^.*\.{INPUT_FILE_EXT}$')

    def __init__(self, source: Path,
                 parser_options: Sequence[str],
                 main_args_parser: CustomArgumentParser):
        Input.__init__(self, source, parser_options, main_args_parser)
        FileDirManager.__init__(self, path=source, for_output=False)

    def _get_input_files(self):
        for element in sorted(self._path.iterdir()):
            if re.fullmatch(rf'^.*\.{self.INPUT_FILE_EXT}$', str(element)):
                yield FileDirManager(path=element, for_output=False).file

    def get_middle_codes(self) -> Iterable[MiddleCode]:
        if self._file:
            for middle_code in self._parser.get_middle_codes(self._file, self._file.name):
                yield middle_code
        else:
            for source in self._get_input_files():
                for middle_code in self._parser.get_middle_codes(source, source.name):
                    yield middle_code
