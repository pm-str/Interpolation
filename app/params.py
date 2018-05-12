import numpy as np
from typing import List


class ConfData:
    def __init__(self, desc, key, value=None, dtype=None, mini=None, maxi=None, select=None):
        self._desc = desc
        self.key = key
        self._value = value
        self.dtype = dtype
        self.maxi = maxi
        self.mini = mini
        self.select = select

    @property
    def type_name(self):
        return self.dtype.__name__

    @property
    def desc(self):
        return f'{self._desc} <{self.type_name}>'

    @property
    def default_value(self):
        return self._value

    @property
    def value(self):
        fd = REQUEST_SETTINGS.get('input_data')
        if fd and fd.get(self.key):
            return fd.get(self.key)
        return self._value


class AlgorithmResult:
    def __init__(self, result, values=None):
        self.result = result
        self.values = values or []
        self.labels = list(range(1, len(values) + 1))
        self.results = [result] * len(values)
        self.iters = len(values)


class RangeResult:
    def __init__(self, values, labels):
        self.values = []
        self.labels = []

        for i, label in zip(values, labels):
            value = i.result if hasattr(i, 'result') else i
            if not self.is_inf(value):
                self.values.append(value)
            else:
                self.values.append(0)
            self.labels.append(label)

    @staticmethod
    def is_inf(value):
        if abs(value) == np.inf:
            return True
        return False


MACKLOREN = 'mackloren'
TEYLOR = 'teylor'
CHEBISHEV = 'chebishev'

ALGORITHMS = {
    MACKLOREN: 'Формула Маклорена',
    TEYLOR: 'Формула Тейлора',
    CHEBISHEV: 'Формулы Чебышева',
}

DEFAULT_RANGE = [
    ConfData('Начало диапазон X0', 'x_start', 0, float),
    ConfData('Конец диапазон Xk', 'x_end', 8, float),
    ConfData('Шаг S', 'step', 1, float),
    ConfData('Количество итераций K', 'k', 5, int),
]

NONE = '–'

PARAMS = {
    MACKLOREN: {
        'CONFIG': [
            ConfData('Количество итераций N', 'n', 15, int),
            ConfData('Окрестность поиска, точка X', 'x', NONE, float),
        ],
        'RANGE': DEFAULT_RANGE
    },
    TEYLOR: {
        'CONFIG': [
            ConfData('Значение функции в точке X0', 'x0', 2, float),
            ConfData('Количество итераций N', 'n', 15, int),
            ConfData('Окрестность поиска, точка X', 'x', NONE, float),
        ],
        'RANGE': DEFAULT_RANGE
    },
    CHEBISHEV: {
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', NONE, float),
            ConfData('Количество итераций N, max(N) = 10', 'n', 15, int),
            ConfData(
                'Тип формулы', 'f_type', 1, int, 1, 5, [
                    'Экспонента', 'Натуральный логорифм', 'Синус', 'Косинус', 'Тангенс',
                ]
            ),
        ],
        'RANGE': DEFAULT_RANGE
    }
}

REQUEST_SETTINGS = {}
