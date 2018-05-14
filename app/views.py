from functools import partial

from django.views.generic import TemplateView, RedirectView

from app.algorithms import ComputationalCluster
from app.helpers import to_lambda, evaluate_range, to_parsed
from app.utils import extract_conf_data, extract_range_data
from app.validators import validate_settings, clear_validators, validate_algo_response
from .params import PARAMS, ALGORITHMS, REQUEST_SETTINGS, RangeResult


class TaskView(TemplateView):
    template_name = 'task.html'


class ResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        clear_validators()
        kwargs['algorithms'] = ALGORITHMS.items()

        return kwargs

    def get(self, request, *args, **kwargs):
        params = dict(request.GET)
        new_context = {}

        formula = params.get('formula', [None])[0]
        if formula and formula in ALGORITHMS.keys():
            CNF = PARAMS[formula]

            new_context['formula'] = (formula, ALGORITHMS[formula])

            new_context['formula_fields'] = CNF['CONFIG']
            new_context['range_fields'] = CNF['RANGE']
            new_context['figure_titles'] = CNF['FIGURE_TITLES']
            new_context['input_data'] = {}
            new_context['func_result'] = {}
            new_context['range_result'] = {}

        expr = params.get('expression')
        if expr:
            new_context['expression'] = expr[0]
            try:
                new_context['func_parsed'] = to_parsed(expr[0])
            except Exception as e:
                print(e)
                REQUEST_SETTINGS['error'] = ("Данное выражение не может быть вычисленно. "
                                             "Проверьте допустимый синтаксис.")

        REQUEST_SETTINGS.update(**new_context)

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
        REQUEST_SETTINGS['func_result'] = None

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
        algo_data['n'] = range_data.get('k', algo_data.get('n'))

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
                REQUEST_SETTINGS['error'] = ('При вычислении функции произошла ошибка. '
                                             'Проверье ограничения.')
                return self.url
            try:
                fn2_res = evaluate_range(**range_data, fn=fn2, param='x')
            except Exception as e:
                print(e)
                REQUEST_SETTINGS['error'] = ('При вычислении апроксимированного значения '
                                             'произошла ошибка. Проверье ограничения.')
                return self.url

            REQUEST_SETTINGS['range_result'] = [fn1_res, fn2_res]

        return self.url
