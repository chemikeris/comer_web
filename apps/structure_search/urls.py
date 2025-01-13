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
        'aligned_structures/<slug:job_id>/<int:result_no>/<int:hit_no>',
        views.aligned_structures,
        name='gtalign_aligned_structures'
        ),
    path(
        'aligned_structures/<slug:job_id>/<int:result_no>',
        views.aligned_structures,
        {'hit_no': 0},
        name='gtalign_aligned_structures_without_hit'
        ),
    path(
        'download/aligned_structures/<slug:job_id>/<int:result_no>/<int:hit_no>',
        views.download_aligned_structures,
        name='download_gtalign_aligned_structures'
        ),
    path(
        'download/input/<slug:job_id>',
        views.download_input,
        name='gtalign_download_input'
        ),
]
