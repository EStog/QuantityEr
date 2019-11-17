from pathlib import Path
from typing import TextIO, Optional

from lib.classes.internal.middle_codes.middle_code import MiddleCode
from lib.classes.outputs.stream_outputs.stream_output import StreamOutput
from lib.utilities.file_dir_manager import FileDirManager


class FileOutput(StreamOutput, FileDirManager):
    OUTPUT_FILE_EXT = 'out'
    SIMULATION_TAG = 'simulation'
    OUTPUT_FILE_FORMAT = f'{{name}}.{OUTPUT_FILE_EXT}'
    OUTPUT_SIMULATION_FILE_FORMAT = f'{{name}}-{SIMULATION_TAG}.{OUTPUT_FILE_EXT}'

    def __init__(self, path: Optional[Path]):
        StreamOutput.__init__(self)
        FileDirManager.__init__(self, path, for_output=True)

    def _get_stream(self, middle_code: MiddleCode, is_simulation: bool) -> TextIO:
        if self._file:
            return self._file
        if self._path:
            name = str(Path(self._path, middle_code.short_name))
        else:
            name = middle_code.full_name
        if is_simulation:
            return FileDirManager(Path(self.OUTPUT_SIMULATION_FILE_FORMAT.format(name=name)),
                                  for_output=True).file
        else:
            return FileDirManager(Path(self.OUTPUT_FILE_FORMAT.format(name=name)),
                                  for_output=True).file
