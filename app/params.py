import numpy as np


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
        fd = REQUEST_SETTINGS.get('input_data', {})
        value = fd.get(self.key)
        if fd and (value or value == 0):
            return fd.get(self.key)
        return self._value


class AlgorithmResult:
    def __init__(self, result, values=None):
        self.result = result
        self.values = values or []
        self.labels = list(range(1, len(self.values) + 1))
        self.results = [result] * len(self.values)
        self.iters = len(self.values)


class RangeResult:
    def __init__(self, values, labels):
        self.values = []
        self.labels = []

        for i, label in zip(values, labels):
            value = i.result if hasattr(i, 'result') else i
            if (isinstance(value, float) or isinstance(value, int)) and not self.is_inf(value):
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
LAGRANZE = 'lagranzh'
EITKEN = 'eitken'
NUETON_ONE = 'nueton_one'
NUETON_TWO = 'nueton_two'
GAUSS = 'gauss'
FIRST_SPLINE = 'first_spline'

ALGORITHMS = {
    MACKLOREN: 'Формула Маклорена',
    TEYLOR: 'Формула Тейлора',
    CHEBISHEV: 'Формулы Чебышева',
    LAGRANZE: 'Многочлен Лагранжа',
    EITKEN: 'Cхема Эйткена',
    NUETON_ONE: 'Первая интер. формула Ньютона',
    NUETON_TWO: 'Вторая интер. формула Ньютона',
    GAUSS: 'Первая интер. формула Гаусса',
    FIRST_SPLINE: 'Ломанный сплайн',
}

DEFAULT_RANGE = [
    ConfData('Начало диапазон X0', 'x_start', 0, float),
    ConfData('Конец диапазон Xk', 'x_end', 8, float),
    ConfData('Шаг S на заданном интервале', 'step', 1, float),
    ConfData('Количество итераций K', 'k', 5, int),
]

NONE = '–'

DEFAULT_TITLES = [[
    'Аппроксимация в точке f(x) n-й итерации',
    'Итоговое значение f(x) в точке X',
], [
    'График функции f(x)',
    'Интерполяция',
]]

SPLINE_TITLES = [[
    'Интерполяционный график f(x+h*n) на шаге n',
    'Значение f(x) в точке x',
], [
    'График функции f(x)',
    'Интерполяция',
]]

PARAMS = {
    MACKLOREN: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 4, float),
            ConfData('Количество итераций N', 'n', 15, int),
        ],
        'RANGE': DEFAULT_RANGE
    },
    TEYLOR: {
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 5, float),
            ConfData('Значение функции в точке X0', 'x0', 2, float),
            ConfData('Количество итераций N', 'n', 15, int),
        ],
        'RANGE': DEFAULT_RANGE
    },
    CHEBISHEV: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': False,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 0.15, float, 0, 1),
            ConfData(
                'Тип формулы', 'f_type', 1, int, 1, 5, [
                    'Экспонента', 'Натуральный логорифм', 'Синус', 'Косинус', 'Тангенс',
                ]
            ),
            ConfData('Допустимое оличество итераций N, max(N) = 10', 'n', 9, int),
        ],
        'RANGE': DEFAULT_RANGE
    },
    LAGRANZE: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': False,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 0.6, float, 0.5, 1.2),
            ConfData(
                'Тип формулы', 'f_type', 1, int, 1, 5, [
                    'Экспонента', 'Синус', 'Косинус', 'Тангенс', 'Натуральный логорифм',
                ]
            ),
            ConfData('Допустимое количество итераций N, max(N) = 8', 'n', 7, int),
        ],
        'RANGE': DEFAULT_RANGE
    },
    EITKEN: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 2.310004, float, -1e3, 1e3),
            ConfData('X начальное в таблице известных значений', 'x_0', 1, float, -1e6, 1e6),
            ConfData('X конечное в таблице известных значений', 'x_n', 3, float, -1e6, 1e6),
            ConfData('Шаг st при генерации таблицы значений', 'st', 0.1, float, 1e-4, 1e3),
        ],
        'RANGE': [
            ConfData('Начало диапазон X0', 'x_start', 1, float),
            ConfData('Конец диапазон Xk', 'x_end', 3, float),
            ConfData('Шаг S на заданном интервале', 'step', 0.2, float),
        ]
    },
    NUETON_ONE: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 1.0001, float, -1e3, 1e3),
            ConfData('X начальное в таблице известных значений', 'x_0', 0, float, -1e6, 1e6),
            ConfData('X конечное в таблице известных значений', 'x_n', 2, float, -1e6, 1e6),
            ConfData('Шаг st при генерации таблицы значений', 'st', 0.1, float, 1e-4, 1e3),
        ],
        'RANGE': [
            ConfData('Начало диапазон X0', 'x_start', 0.1, float),
            ConfData('Конец диапазон Xk', 'x_end', 1.9, float),
            ConfData('Шаг S на заданном интервале', 'step', 0.2, float),
        ]
    },
    NUETON_TWO: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 2.310004, float, -1e3, 1e3),
            ConfData('X начальное в таблице известных значений', 'x_0', 1, float, -1e6, 1e6),
            ConfData('X конечное в таблице известных значений', 'x_n', 5, float, -1e6, 1e6),
            ConfData('Шаг st при генерации таблицы значений', 'st', 0.1, float, 1e-4, 1e3),
        ],
        'RANGE': [
            ConfData('Начало диапазона X0', 'x_start', 1, float),
            ConfData('Конец диапазона Xk', 'x_end', 5, float),
            ConfData('Шаг S на заданном интервале', 'step', 0.5, float),
        ]
    },
    GAUSS: {
        'FIGURE_TITLES': DEFAULT_TITLES,
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 1, float, -1e3, 1e3),
            ConfData('X начальное в таблице известных значений', 'x_0', 1.15, float, -1e6, 1e6),
            ConfData('Количество шагов n', 'n', 10, int, -1000, 1000),
            ConfData('Шаг h в формуле x = x0 + th', 'h', 0.1, float, 1e-4, 1e3),
        ],
        'RANGE': [
            ConfData('Начало диапазон X0', 'x_start', 0, float),
            ConfData('Конец диапазон Xk', 'x_end', 1, float),
            ConfData('Шаг S при сравнении значений на заданном интервале', 'step', 0.1, float),
        ]
    },
    FIRST_SPLINE: {
        'FIGURE_TITLES': SPLINE_TITLES,
        'FUNCTION_REQUIRED': True,
        'CONFIG': [
            ConfData('Окрестность поиска, точка X', 'x', 1, float, -1e3, 1e3),
            ConfData('X начальное в таблице известных значений', 'x_0', 0.67, float, -1e6, 1e6),
            ConfData('Шаг h в формуле x = x0 + th', 'h', 0.1, float, 1e-4, 1e3),
        ],
        'RANGE': [
            ConfData('Начало диапазон X0', 'x_start', 0, float),
            ConfData('Конец диапазон Xk', 'x_end', 1, float),
            ConfData('Шаг S при сравнении значений на заданном интервале', 'step', 0.1, float),
        ]
    },
}

REQUEST_SETTINGS = {}
