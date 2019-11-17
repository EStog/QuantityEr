from pathlib import Path
from typing import Optional

from lib.utilities.logging import ExitCode
from lib.utilities.logging.with_logging import WithLogging


class FileDirManager(WithLogging):

    def __init__(self, path: Optional[Path], for_output: bool):
        WithLogging.__init__(self)
        self._path = path
        self._file = None
        if self._path:
            if self._is_file(for_output):
                if for_output:
                    self._open_file('a')
                else:
                    self._open_file('r')

    @property
    def path(self):
        return self._path

    @property
    def file(self):
        return self._file

    def _is_file(self, create: bool):
        """
        Returns True if path is a file, else returns False.
        Creates the path if it does not exists
        """
        if not self._path.exists():
            if create:
                try:
                    self._path.touch()
                    return True
                except FileNotFoundError:
                    try:
                        self._path.mkdir(parents=True)
                        return False
                    except OSError as e:
                        self._critical(f'Cannot create directory {self._path} for outputs',
                                       ExitCode.FILE_ERROR, e)
            else:
                self._critical(f'Path not found', ExitCode.FILE_ERROR, self._path)
        else:
            return self._path.is_file()

    def _open_file(self, mode: str):
        try:
            self._file = self._path.open(mode)
        except OSError as e:
            self._critical(f'Cannot open file {self._path.name}',
                           ExitCode.FILE_ERROR, e)
