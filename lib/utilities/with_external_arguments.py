from abc import ABC, abstractmethod
from typing import Union, Callable


class WithExternalArguments(ABC):
    """This class manage its defaults in a way that can be presented to the outside"""

    def get_defaults_info(self):
        ...

    def get_info(self):
        return f'Info for {self.__class__.__name__}:\n\t{self.__doc__}'

    def __init__(self, **kwargs):
        """Initializes the arguments that are None if a default value has been given.
        Otherwise the value remains None"""
        self._set_attributes(**kwargs)

    @abstractmethod
    def _init_parameters(self):
        """
        Define here the arguments the class must accept from the user.
        Each option must be a protected attribute of type Argument.
        See the GithubEngine for an example
        """
        pass

    def _set_attributes(self, **kwargs):
        """
        Sets the appropriated values for the received options.
        Each option is set as an attribute of the class.
        In case an invalid option is present or an obligatory one
        has not been provided, an AttributeError exception with a
        corresponding message is raised
        """
        self._init_parameters()
        for key in kwargs:
            try:
                attr = getattr(self, f'_{key}')
            except AttributeError:
                raise AttributeError(f'{self.__class__.__name__} does not expects parameter {key}')
            if isinstance(attr, ExternalArgument):
                if isinstance(kwargs[key], str):
                    setattr(self, f'_{key}', attr.type_caster(kwargs[key]))
                else:
                    setattr(self, f'_{key}', kwargs[key])
            else:
                raise AttributeError(f'{self.__class__.__name__} does not expects parameter {key}')
        missing = set()
        for key in self.__dict__:
            attr = getattr(self, key)
            if isinstance(attr, ExternalArgument):
                if attr.obligatory:
                    missing.add(key[1:])
                else:
                    setattr(self, key, attr.default)
        if missing:
            raise AttributeError(f'Parameters {missing!s} not provided for {self.__class__.__name__}')

    @staticmethod
    def _get_value(default, value):
        return default if value is None else value


class ExternalArgument:
    def __init__(self, type_caster: Union[type, Callable[[str], object]],
                 default: object = None, obligatory: bool = False):
        self.type_caster = type_caster
        self.default = default
        self.obligatory = obligatory
