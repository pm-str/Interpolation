from functools import partial

from django.views.generic import TemplateView, RedirectView

from app.algorithms import ComputationalCluster
from app.helpers import to_lambda, evaluate_range
from app.utils import to_value, extract_conf_data, extract_range_data
from app.validators import validate_settings, clear_validators, validate_algo_response
from .params import PARAMS, ALGORITHMS, REQUEST_SETTINGS, REQUEST_QUERY, RangeResult


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
            CNF = PARAMS[formula]

            new_context['formula'] = (formula, ALGORITHMS[formula])
            new_query['formula'] = formula

            new_context['formula_fields'] = CNF['CONFIG']
            new_context['range_fields'] = CNF['RANGE']

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
        REQUEST_SETTINGS.clear()

        return self.url


class EvalFormulaView(RedirectView):
    url = '/result'

    def get_redirect_url(self, *args, **kwargs):
        get_data = self.request.GET

        REQUEST_SETTINGS['success'] = True

        algo_data = extract_conf_data(get_data)

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

        return self.url


class ConfigDefaultView(RedirectView):
    url = '/result'

    def get_redirect_url(self, *args, **kwargs):
        formula = REQUEST_SETTINGS.get('formula')
        if not formula:
            REQUEST_SETTINGS['warning'] = 'Не установленна формула'
        else:
            CNF = PARAMS[formula[0]]
            for i in CNF['CONFIG']:
                REQUEST_SETTINGS['input_data'][i.key] = i.default_value

        return self.url


class RangeDefaultView(RedirectView):
    url = '/result'

    def get_redirect_url(self, *args, **kwargs):
        formula = REQUEST_SETTINGS.get('formula')
        if not formula:
            REQUEST_SETTINGS['warning'] = 'Не установленна формула'
        else:
            CNF = PARAMS[formula[0]]
            for i in CNF['RANGE']:
                REQUEST_SETTINGS['input_data'][i.key] = i.default_value

        return self.url


class EvalRangeView(RedirectView):
    url = '/result'

    def partial_formula(self, algo_data, expression, formula):
        data = {i: j for i, j in algo_data.items()}
        cc = ComputationalCluster(expression)
        alg = getattr(cc, formula)
        return partial(alg, **data)

    def get_redirect_url(self, *args, **kwargs):
        get_data = self.request.GET

        REQUEST_SETTINGS['success'] = True

        range_data = extract_range_data(get_data)
        algo_data = REQUEST_SETTINGS['input_data']
        algo_data.update(range_data)
        algo_data = extract_conf_data(algo_data)

        is_valid = validate_settings()
        if is_valid:
            expression = REQUEST_SETTINGS['expression']
            formula = REQUEST_SETTINGS['formula'][0]
            fn1 = to_lambda(expression)
            fn2 = self.partial_formula(algo_data, expression, formula)

            try:
                fn1_res = evaluate_range(**range_data, fn=fn1)
            except Exception as e:
                print(e)
                REQUEST_SETTINGS['error'] = ('При вычислении апроксимированного значения '
                                             'произошла ошибка. Проверье ограничения.')
                return self.url
            try:
                fn2_res = evaluate_range(**range_data, fn=fn2, param='x')
            except Exception as e:
                print(e)
                REQUEST_SETTINGS['error'] = ('При вычислении функции произошла ошибка. '
                                             'Проверье ограничения.')
                return self.url

            REQUEST_SETTINGS['range_result'] = RangeResult(fn1_res, fn2_res)

        return self.url
