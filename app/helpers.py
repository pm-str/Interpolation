from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol, lambdify

from app.utils import TRANSFORMATIONS


def to_lambda(str_func, trans=TRANSFORMATIONS, symbol=Symbol('x')):
    func = parse_expr(str_func, transformations=trans)
    return lambdify(symbol, func, 'numpy')


def evaluate_range(x_start, x_end, step, fn, param=None):
    """Array of function's results

    Arguments:
        param: name of the argument, for example, 'x'
    """

    res = []
    x = x_start
    while x < x_end:
        if param:
            data = {param: x}
            res.append(fn(**data))
        else:
            res.append(fn(x))
        x += step

    return res
