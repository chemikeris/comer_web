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
        'detailed/<slug:job_id>/<int:result_no>',
        views.detailed,
        name='gtalign_detailed'
        ),
    path(
        'download/input/<slug:job_id>',
        views.download_input,
        name='gtalign_download_input'
        ),
    path(
        'download/input/<slug:job_id>/<int:result_no>',
        views.download_input,
        name='download_gtalign_input_given_result_no'
        ),
    path(
        'download/results/<slug:job_id>',
        views.download_results,
        name='download_gtalign_results_zip'
        ),
    path(
        'download/results/<slug:job_id>/<int:result_no>',
        views.download_results,
        name='download_gtalign_results_json_for_query'
        ),
    path('api/submit', views.api_submit, name='gtalign_api_submit'),
    path(
        'api/job_status/<slug:job_id>',
        views.api_job_status,
        name='gtalign_api_job_status'
        ),
    path(
        'api/available_databases',
        views.api_available_databases,
        name='gtalign_api_databases'
        ),
]
