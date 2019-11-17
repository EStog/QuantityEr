from pathlib import Path

from lib.utilities.logging.with_logging import WithLogging


class MiddleCode(WithLogging):
    MIDDLE_CODE_NAME_FORMAT = '{namespace}.{name}'

    def __init__(self, namespace: str, name: str):
        WithLogging.__init__(self)
        self._namespace = namespace
        self._name = name
        self.original_query = ''
        self._full_name = self.MIDDLE_CODE_NAME_FORMAT.format(namespace=namespace, name=name)
        self._short_name = self.MIDDLE_CODE_NAME_FORMAT.format(
            namespace=Path(namespace).name,
            name=name
        )

    @property
    def full_name(self):
        return self._full_name

    @property
    def short_name(self):
        return self._short_name

    @property
    def namespace(self):
        return self._namespace

    @property
    def name(self):
        return self._name
