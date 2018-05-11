import numpy as np
from typing import List


class ConfData:
    def __init__(self, desc, key, value=None, dtype=None):
        self._desc = desc
        self.key = key
        self._value = value
        self.dtype = dtype

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


class RangeResult:
    def __init__(self, values1, values2: List[AlgorithmResult], labels1=None, labels2=None):
        self.values1 = values1
        self.values2 = [i.result for i in values2]
        self.labels1 = labels1
        self.labels2 = labels2


        if not labels1:
            self.set_labels1()

        if not labels2:
            self.set_labels2()

    def set_labels1(self, start=1, end=None, step=1):
        end = (end or len(self.values1)) + 1
        self.labels1 = list(np.arange(start, end, step))

    def set_labels2(self, start=1, end=None, step=1):
        end = (end or len(self.values2)) + 1
        self.labels2 = list(np.arange(start, end, step))


MACKLOREN = 'mackloren'
TEYLOR = 'teylor'

ALGORITHMS = {
    MACKLOREN: 'Формула Маклорена',
    TEYLOR: 'Формула Тейлора',
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
    }
}

REQUEST_SETTINGS = {}
