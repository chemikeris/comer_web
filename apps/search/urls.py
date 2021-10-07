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
    # API URLs start here
    path('api/submit', views.submit, name='api_submit'),
    path(
        'api/job_status/<slug:job_id>',
        views.ApiJobStatus.as_view(),
        name='api_job_status'
        ),
    path(
        'api/results_json/<slug:job_id>',
        views.ApiResultsJson.as_view(),
        name='api_results_json'
        ),
    path(
        'api/results_zip/<slug:job_id>',
        views.ApiResultsZip.as_view(),
        name='api_results_zip'
        ),
    path(
        'api/job_input/<slug:job_id>',
        views.ApiJobInput.as_view(),
        name='api_job_input'
        ),
    path(
        'api/job_options/<slug:job_id>',
        views.ApiJobOptions.as_view(),
        name='api_job_options'
        ),
    path(
        'api/job_error/<slug:job_id>',
        views.ApiJobError.as_view(),
        name='api_job_error'
        ),
]
