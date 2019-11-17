from abc import ABC
from typing import Sequence

from lib.utilities.logging.with_logging import WithLogging
from lib.utilities.with_external_arguments import WithExternalArguments


class WithLoggingAndExternalArguments(WithLogging, WithExternalArguments, ABC):

    def __init__(self, args_sequence: Sequence = ()):
        WithLogging.__init__(self)
        WithExternalArguments.__init__(self, args_sequence=args_sequence,
                                       prefix_chars='*', fromfile_prefix_chars='$',
                                       version_arguments=('*v', '**version'))
