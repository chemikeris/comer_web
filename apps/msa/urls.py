from django.urls import path

from . import views

urlpatterns = [
    path('submit/', views.submit, name='submit_msa'),
    path(
        'show/<slug:msa_job_id>/',
        views.show,
        name='show_msa'
        ),
    path(
        'download/<slug:msa_job_id>/',
        views.download,
        name='download_msa'
        ),
]
