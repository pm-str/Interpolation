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
            except Exception as e:
                return e

            result += lambda_result / fact_v * ((x - x0) ** i)
            intermediate_res.append(result)

        return AlgorithmResult(result, intermediate_res)

    def mackloren(self, x, n):
        return self.teylor(x=x, x0=0, n=n)


if __name__ == '__main__':
    cc = ComputationalCluster('e^x')
    print(cc.teylor(1/2, 0, 15))