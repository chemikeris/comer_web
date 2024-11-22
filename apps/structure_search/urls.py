from django.urls import path

from . import views

urlpatterns = [
    path('', views.input, name='gtalign_input'),
    path('input/', views.input, name='gtalign_input'),
    path(
        'results/<slug:job_id>',
        views.results,
        {'redirect_to_first': True},
        name='gtalign_results'
        ),
    path(
        'detailed/<slug:job_id>/<int:sequence_no>', views.detailed,
        name='gtalign_detailed'
        ),
]
