from typing import Iterable

from lib.utilities.with_external_arguments import CustomArgumentParser


def get_component_caster(d: dict, name: str):
    def func(a):
        if func.cast:
            func.cast = False
            if a not in d:
                func.__name__ = name
                raise TypeError
            else:
                return d[a]
        else:
            return a

    func.cast = True
    return func


def get_tuple_caster(*casters):
    def func(a):
        caster = casters[func.i]
        try:
            func.__name__ = caster.__name__
        except AttributeError:
            pass
        func.i += 1
        if func.i == len(casters):
            func.i = 0
        return caster(a)

    func.i = 0
    return func


def get_dict_caster(d):
    def func(key):
        if key in d:
            return d[key]
        else:
            raise TypeError

    return func


def get_caster_to_optional(type_caster):
    def f(value: str):
        if not value:
            return value
        else:
            return type_caster(value)

    return f


def get_included_excluded_principle_iter_amount(n: int):
    r = 0
    for p in range(1, n + 1):
        r += combination_amount(n, p)
    return r


def combination_amount(n: int, p: int) -> int:
    n_p = n - p
    numerator_init = max(p, n_p)
    denominator_end = min(p, n_p)
    num = 1
    for i in range(numerator_init + 1, n + 1):
        num *= i
    den = 1
    for i in range(1, denominator_end + 1):
        den *= i
    return num // den


def div(a: int, b: int):
    return a / b if b != 0 else 0


def quote(message, quote_format='<{}>'):
    return quote_format.format(message)


def get_members_set_string(l: Iterable):
    s = ''
    for e in l:
        s += f'{str(e)}, '
    return f'{{{s[:-2]}}}'


def get_component(component_options, type_dict: dict,
                  component: str, args_parser: CustomArgumentParser,
                  **kwargs):
    type_name, options = get_type_and_options(component_options)
    if type_name not in type_dict:
        args_parser.error(
            f'Invalid {component} type: {type_name}. '
            f'{component.capitalize()} type must be one of {set(type_dict.keys())!s}')
    return type_dict[type_name](options, **kwargs)


def get_type_and_options(options):
    if not isinstance(options, str):
        return options[0], options[1:]
    else:
        return options, ()
