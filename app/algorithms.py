from typing import Callable
from sympy import Symbol, lambdify, Add
from sympy.parsing.sympy_parser import parse_expr

from app.params import AlgorithmResult
from app.utils import *


class ComputationalCluster:
    def __init__(self, func: str, variable: str = 'x'):
        self.str_func: str = func
        self._parsed_func: Callable = None
        self.symbol = Symbol(variable)

    @property
    def parsed_func(self):
        if not self._parsed_func:
            try:
                self._parsed_func = self.parse_func()
            except Exception as e:
                return e
        return self._parsed_func

    def derivative(self, func: Add, symbols=None, n=None, start=1, end=int(1e9)):
        symbols = symbols or self.symbol
        der_func = func

        if n:
            return der_func.diff(symbols, n)

        for i in range(start, end):
            yield der_func
            der_func = der_func.diff(symbols)

    @staticmethod
    def fact(start=1, end=int(1e9)):
        fact = 1

        for i in range(start, end):
            yield fact
            fact *= i

    def lambda_func(self, func, symbols=None):
        symbols = symbols or self.symbol
        return lambdify(symbols, func, 'numpy')

    def parse_func(self, transforms=TRANSFORMATIONS):
        self._parsed_func = parse_expr(self.str_func, transformations=transforms)
        return self.parsed_func

    def teylor(self, x, x0, n=ITERATIONS):
        intermediate_res = []
        result = 0
        func = self.derivative(self.parsed_func)
        fact = self.fact()

        for i in range(0, n):
            func_v = next(func)
            fact_v = next(fact)
            try:
                lambda_result = self.lambda_func(func_v, Symbol('x'))(x0)
                if 'inf' in str(lambda_result):
                    return AssertionError(
                        'Выполнено деление на ноль. Измените выражение или поменяйте метод',
                        str(lambda_result),
                    )
            except Exception as e:
                return e

            result += lambda_result / fact_v * ((x - x0) ** i)
            intermediate_res.append(result)

        return AlgorithmResult(result, intermediate_res)

    def mackloren(self, x, n):
        return self.teylor(x=x, x0=0, n=n)

    def lagranzh(self, x):
        pass

    def chebishev(self, x, f_type, n=100):
        def fn(x, iters, a):
            result = 0
            ar = []

            for i in range(min(iters, len(a))):
                result += a[i] * x ** i
                ar.append(result)

            return AlgorithmResult(result, ar)

        if f_type == 1:
            a = [0.9999998, 1.0000000, 0.5000063, 0.1666674, 0.0416350,
                 0.0083298, 0.0014393, 0.0002040]
            return fn(x, n, a)
        if f_type == 2:
            a = [0.999981028, -0.499470150, 0.328233122,
                 0.225873284, 0.134639267, -0.055119959, 0.010757369]
            return fn(x, n, a)
        if f_type == 3:
            a = [1.00000002, -0.166666589, -0.000198107, 0.008333075, 0.000002608]
            return fn(x, n, a)
        if f_type == 4:
            a = [1.000000000000, -0.499999999942, 0.041666665950, -0.001388885683,
                 0.000024795132, -0.000000269591]
            return fn(x, n, a)
        if f_type == 5:
            a = [1.00000002, 0.33333082, 0.13339762, 0.05935836, 0.02457096, 0.00294045, 0.00947324]
            return fn(x, n, a)


if __name__ == '__main__':
    cc = ComputationalCluster('e^x')
    print(cc.teylor(1 / 2, 0, 15))
