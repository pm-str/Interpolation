from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication,
    convert_xor,
    implicit_application,
    function_exponentiation,
    implicit_multiplication_application,
)

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
