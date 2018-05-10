from django.urls import path
from django.views.generic import RedirectView
from .views import ResultView, AdditionalView, ClearParamsView, EvaluteView

from app.views import TaskView

urlpatterns = [
   path('', RedirectView.as_view(url='/task')),
   path('task', TaskView.as_view()),
   path('result', ResultView.as_view()),
   path('additional', AdditionalView.as_view()),
   path('clear', ClearParamsView.as_view()),
   path('evaluate', EvaluteView.as_view()),
]
