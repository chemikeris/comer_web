from django.urls import path

from . import views

urlpatterns = [
    path('', views.input, name='input'),
    path('input/', views.input, name='input'),
    path(
        'results/<slug:job_id>',
        views.results,
        {'redirect_to_first': True},
        name='results'
        ),
    path(
        'results/summary/<slug:job_id>',
        views.results,
        name='results_summary'
        ),
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
    #
    # API URLs start here
    #
    # Submit job:
    path('api/submit', views.submit, name='api_submit'),
    # Check status and get all results:
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
    # Download files for all queries:
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
    # Download detailed files for single query:
    path(
        'api/detailed_input/<slug:job_id>/<int:sequence_no>',
        views.ApiDetailedDownloadInput.as_view(),
        name='api_detailed_input'
        ),
    path(
        'api/detailed_json/<slug:job_id>/<int:sequence_no>',
        views.ApiDetailedDownloadJSON.as_view(),
        name='api_detailed_json'
        ),
    path(
        'api/detailed_profile/<slug:job_id>/<int:sequence_no>',
        views.ApiDetailedDownloadProfile.as_view(),
        name='api_detailed_profile'
        ),
    path(
        'api/detailed_msa/<slug:job_id>/<int:sequence_no>',
        views.ApiDetailedDownloadMSA.as_view(),
        name='api_detailed_msa'
        ),
]
