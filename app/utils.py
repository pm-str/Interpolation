from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication,
    convert_xor,
    implicit_application,
    function_exponentiation,
    implicit_multiplication_application,
)

from app.params import REQUEST_SETTINGS

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication,
    convert_xor,
    implicit_application,
    function_exponentiation,
    implicit_multiplication_application,
)
ITERATIONS = 5


def ignore_exception(IgnoreException=Exception, DefaultVal=None):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    """

    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal

        return _dec

    return dec


to_value = ignore_exception(ValueError)


def extract_conf_data(get_data):
    algo_data = {}

    for field in REQUEST_SETTINGS.get('formula_fields', []):
        key = field.key
        value = get_data.get(key)
        dtype = field.dtype or float
        svalue = to_value(dtype)(value)
        if not value:
            REQUEST_SETTINGS['error'] = 'Ошибка. Введите недостающие данные'
        elif not svalue and svalue != 0:
            print(value, dtype, key)
            REQUEST_SETTINGS['error'] = (f'Ошибка. Неверный тип данных <{key}>. '
                                         'Обратитесь к описанию параметров')
        else:
            algo_data[key] = to_value(dtype)(value)

    if 'input_data' not in REQUEST_SETTINGS:
        REQUEST_SETTINGS['input_data'] = {}

    REQUEST_SETTINGS['input_data'].update(**algo_data)

    return algo_data


def extract_range_data(get_data):
    algo_data = {}

    for field in REQUEST_SETTINGS.get('range_fields', []):
        key = field.key
        value = get_data.get(key)
        dtype = field.dtype or float
        svalue = to_value(dtype)(value)
        if not value:
            REQUEST_SETTINGS['error'] = 'Ошибка. Введите недостающие данные'
        elif not svalue and svalue != 0:
            print(value, dtype, key)
            REQUEST_SETTINGS['error'] = (f'Ошибка. Неверный тип данных <{key}>. '
                                         'Обратитесь к описанию параметров')
        else:
            algo_data[key] = to_value(dtype)(value)

    if 'input_data' not in REQUEST_SETTINGS:
        REQUEST_SETTINGS['input_data'] = {}

    REQUEST_SETTINGS['input_data'].update(**algo_data)
    return algo_data
