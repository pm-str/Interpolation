from django.views.generic import TemplateView, RedirectView

from app.algorithms import ComputationalCluster
from app.utils import to_value
from app.validators import validate_settings, clear_validators, validate_algo_response
from .params import PARAMS, ALGORITHMS, REQUEST_SETTINGS, REQUEST_QUERY


class TaskView(TemplateView):
    template_name = 'task.html'


class ResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        clear_validators()
        kwargs['algorithms'] = ALGORITHMS.items()
        kwargs['query_params'] = REQUEST_QUERY.items()

        return kwargs

    def get(self, request, *args, **kwargs):
        params = dict(request.GET)
        new_context = {}
        new_query = {}

        formula = params.get('formula', [None])[0]
        if formula and formula in ALGORITHMS.keys():
            new_context['formula'] = (formula, ALGORITHMS[formula])
            new_query['formula'] = formula

            new_context['formula_fields'] = PARAMS[formula]

        expr = params.get('expression')
        if expr:
            new_context['expression'] = expr[0]
            new_query['expression'] = expr[0]

        REQUEST_SETTINGS.update(**new_context)
        REQUEST_QUERY.update(**new_query)

        context = self.get_context_data(**kwargs, **REQUEST_SETTINGS)

        return self.render_to_response(context)


class AdditionalView(TemplateView):
    template_name = 'additional.html'


class ClearParamsView(RedirectView):
    url = '/result'

    def get_redirect_url(self, *args, **kwargs):
        url = super().get_redirect_url(args, kwargs)

        REQUEST_SETTINGS.clear()

        return url


class EvaluteView(RedirectView):
    url = '/result'

    def get_redirect_url(self, *args, **kwargs):
        url = super().get_redirect_url(args, kwargs)
        get_data = self.request.GET
        algo_data = {}

        REQUEST_SETTINGS['success'] = True

        for field in REQUEST_SETTINGS.get('formula_fields', []):
            key = field.key
            value = get_data.get(key)
            dtype = field.dtype or float
            if not value:
                REQUEST_SETTINGS['error'] = 'Ошибка. Введите недостающие данные'
            elif not to_value(dtype)(value):
                print(value, dtype, key)
                REQUEST_SETTINGS['error'] = ('Ошибка. Неверный тип данных.'
                                             'допускается использование (int, float)')
            else:
                algo_data[key] = to_value(dtype)(value)
        if 'formula_data' not in REQUEST_SETTINGS:
            REQUEST_SETTINGS['formula_data'] = {}

        REQUEST_SETTINGS['formula_data'].update(**algo_data)

        is_valid = validate_settings()
        if is_valid:
            expression = REQUEST_SETTINGS['expression']
            formula = REQUEST_SETTINGS['formula'][0]
            data = {i: j for i, j in algo_data.items()}
            cc = ComputationalCluster(expression)
            alg = getattr(cc, formula)
            result = alg(**data)

            is_valid = validate_algo_response(result)
            if is_valid:
                REQUEST_SETTINGS['func_result'] = result
            else:
                REQUEST_SETTINGS['func_result'] = None

        return url
