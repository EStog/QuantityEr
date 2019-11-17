from enum import Enum


class XEnum(Enum):

    @property
    def name(self):
        return self._name_.lower()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def cast_from_name(cls, name: str):
        name = name.upper()
        if name in cls.__members__:
            return cls.__members__[name]
        else:
            raise TypeError(f'{name} is not member of {cls.__name__}')

    @classmethod
    def default(cls):
        if 'DEFAULT' in cls.__members__:
            return cls.DEFAULT.name
        else:
            raise KeyError(f'Enum {cls.__name__} has no default')
