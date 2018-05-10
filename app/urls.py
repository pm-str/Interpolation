from django.urls import path
from django.views.generic import RedirectView
from .views import (ResultView, AdditionalView, ClearParamsView,
                    EvalFormulaView, RangeDefaultView, ConfigDefaultView, EvalRangeView)

from app.views import TaskView

urlpatterns = [
    path('', RedirectView.as_view(url='/task')),
    path('task', TaskView.as_view()),
    path('result', ResultView.as_view()),
    path('additional', AdditionalView.as_view()),
    path('clear', ClearParamsView.as_view()),
    path('default/conf', ConfigDefaultView.as_view()),
    path('default/range', RangeDefaultView.as_view()),
    path('eval/formula', EvalFormulaView.as_view()),
    path('eval/range', EvalRangeView.as_view()),
]
