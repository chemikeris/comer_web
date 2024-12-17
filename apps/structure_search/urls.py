from django.urls import path

from . import views

urlpatterns = [
    path('', views.input, name='gtalign_index'),
    path('input/', views.input, name='gtalign_input'),
    path(
        'results/<slug:job_id>',
        views.results,
        name='gtalign_results'
        ),
    path(
        'results/<slug:job_id>',
        views.results,
        name='gtalign_results_summary'
        ),
    path(
        'detailed/<slug:job_id>/<int:result_no>', views.detailed,
        name='gtalign_detailed'
        ),
]
