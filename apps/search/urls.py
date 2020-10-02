from django.urls import path

from . import views

urlpatterns = [
    path('', views.input, name='input'),
    path('input/', views.input, name='input'),
    path('results/<slug:job_id>', views.results, name='results'),
    path(
        'detailed/<slug:job_id>/<int:sequence_no>', views.detailed,
        name='detailed'
        )
]
