from django.urls import path

from . import views

urlpatterns = [
    path('', views.input, name='input'),
    path('input/', views.input, name='input'),
    path('results/<slug:job_id>', views.results, name='results'),
    path(
        'results/input/<slug:job_id>/',
        views.show_input,
        name='results_show_input'
        ),
    path(
        'detailed/<slug:job_id>/<int:sequence_no>', views.detailed,
        name='detailed'
        ),
    path(
        'detailed/input/<slug:job_id>/<int:sequence_no>',
        views.show_input,
        name='detailed_show_input'
        ),
]
