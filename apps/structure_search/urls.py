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
        'download/aligned_structures_reference/<slug:job_id>/<int:result_no>/<int:hit_no>',
        views.download_aligned_structure,
        name='download_gtalign_aligned_structure_reference'
        ),
    path(
        'download/aligned_structures_query/<slug:job_id>/<int:result_no>',
        views.download_input,
        name='download_gtalign_aligned_structure_query'
        ),
    path(
        'download/input/<slug:job_id>',
        views.download_input,
        name='gtalign_download_input'
        ),
    path(
        'download/aligned_structures_multiple/',
        views.download_aligned_structures_multiple,
        name='gtalign_download_aligned_structures_multiple'
        ),
]
