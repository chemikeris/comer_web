from django.urls import path

from . import views

urlpatterns = [
    path('submit/', views.submit, name='submit_msa'),
    path(
        'show/<slug:msa_job_id>/',
        views.show,
        name='show_msa'
        ),
]
