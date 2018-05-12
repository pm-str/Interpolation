import numpy as np
import warnings
from typing import Callable

from collections import defaultdict
from sympy import Symbol, lambdify, Add
from sympy.parsing.sympy_parser import parse_expr

from app.messages import FUNC_DOES_NOT_EXIST, ZERO_DIVISION
from app.params import AlgorithmResult
from app.utils import *

warnings.filterwarnings('error')


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
                        ZERO_DIVISION,
                        str(lambda_result),
                    )
            except Exception as e:
                return e

            result += lambda_result / fact_v * ((x - x0) ** i)
            intermediate_res.append(result)

        return AlgorithmResult(result, intermediate_res)

    def mackloren(self, x, n):
        return self.teylor(x=x, x0=0, n=n)

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
        elif f_type == 2:
            a = [0.999981028, -0.499470150, 0.328233122,
                 0.225873284, 0.134639267, -0.055119959, 0.010757369]
        elif f_type == 3:
            a = [1.00000002, -0.166666589, -0.000198107, 0.008333075, 0.000002608]
        elif f_type == 4:
            a = [1.000000000000, -0.499999999942, 0.041666665950, -0.001388885683,
                 0.000024795132, -0.000000269591]
        else:
            a = [1.00000002, 0.33333082, 0.13339762, 0.05935836, 0.02457096, 0.00294045, 0.00947324]

        return fn(x, n, a)

    def lagranzh(self, x, f_type, n=100):
        xs = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

        def fn(x, iters, xs, ys):
            result = 0
            ar = []

            for i in range(min(iters, len(ys))):
                x_res = 1
                for j in range(len(xs)):
                    if i != j:
                        x_res *= (x - xs[j]) / (xs[i] - xs[j])

                result += ys[i] * x_res
                ar.append(result)

            return AlgorithmResult(result, ar)

        if f_type == 1:
            ys = [1.64872, 1.82212, 2.01375, 2.22554, 2.45960, 2.71828, 3.004717, 3.32012]
        elif f_type == 2:
            ys = [0.47943, 0.56464, 0.64422, 0.71736, 0.78333, 0.84147, 0.89121, 0.93204]
        elif f_type == 3:
            ys = [0.87758, 0.82534, 0.76484, 0.69671, 0.62161, 0.54030, 0.45360, 0.36236]
        elif f_type == 4:
            ys = [0.54630, 0.68414, 0.84229, 1.02964, 1.26016, 1.55741, 1.96476, 2.57215]
        else:
            ys = [-0.69315, -0.51083, -0.35667, -0.22314, -0.10536, 0, 0.09531, 0.18232]

        return fn(x, n, xs, ys)

    def eitken(self, x, x_0, x_n, st, *args, **kwargs):
        xs = list(np.arange(x_0, x_n, st))
        func = self.lambda_func(self.parsed_func, Symbol('x'))
        try:
            ys = [func(i) for i in xs]
        except Exception as e:
            print(e)
            return AssertionError(FUNC_DOES_NOT_EXIST, None)
        
        ps = ys.copy()
        values = []

        k = 1
        while k < len(ys):
            tmp = []
            for i in range(len(ys) - k):
                try:
                    m_res = 1/(xs[i+k]-xs[i]) * (ps[i] * (xs[i+k]-x) - ps[i+1] * (xs[i]-x))
                except RuntimeWarning as e:
                    print(e)
                    return e
                tmp.append(m_res)

            k += 1
            ps = tmp.copy()
            values.append(ps[0])

    def get_q(self, x, xs, h, first=False):
        q = (x - (xs[0] if first else xs[-1])) / h

        yield 1

        k = 0
        res = 1

        while True:
            res *= (q+k)
            k = k - 1 if first else k + 1
            yield res

    def get_diff(self, ys, first=False):
        def calc(dg, n):
            if dg == 0:
                return ys[n]
            elif n in hash.get(dg, {}):
                return hash[dg][n]
            else:
                hash[dg][n] = calc(dg-1, n+1) - calc(dg-1, n)

            return hash[dg][n]

        if first:
            yield ys[0]
            ind = 0
            degree = 1
        else:
            yield ys[-1]
            ind = len(ys) - 2
            degree = 1

        hash = defaultdict(dict)

        while True:
            yield calc(degree, ind)
            degree += 1
            ind = ind + 0 if first else ind - 1

    def nueton(self, x, x_0, x_n, st, first=False, **kwargs):
        xs = list(np.arange(x_0, x_n, st))
        func = self.lambda_func(self.parsed_func, Symbol('x'))
        try:
            ys = [func(i) for i in xs]
        except Exception as e:
            print(e)
            return AssertionError(FUNC_DOES_NOT_EXIST, None)

        res = 0
        values = []
        h = st

        q = self.get_q(x, xs, h, first)

        diff = self.get_diff(ys, first)
        fact = self.fact()

        for i in range(len(ys)):
            q_res = next(q)
            diff_res = next(diff)
            fact_res = next(fact)

            res += diff_res * q_res/fact_res
            values.append(res)

        return AlgorithmResult(res, values)

    def nueton_one(self, *args, **kwargs):
        kwargs.update({'first': True})
        return self.nueton(*args, **kwargs)

    def nueton_two(self, *args, **kwargs):
        return self.nueton(*args, **kwargs)


if __name__ == '__main__':
    cc = ComputationalCluster('E^x')
    print(cc.nueton_one(1, 0.5, 1.3, 0.1).result)
    print(cc.nueton_two(1, 0.5, 1.3, 0.1).result)
