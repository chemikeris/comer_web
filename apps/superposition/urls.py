from django.urls import path

from . import views

urlpatterns = [
    path(
        'aligned_structures/<slug:structure_search_job_id>/<int:result_no>/<int:hit_no>',
        views.aligned_structures,
        name='gtalign_aligned_structures'
        ),
    path(
        'aligned_structures/<slug:structure_search_job_id>/<int:result_no>',
        views.aligned_structures,
        {'hit_no': 0},
        name='gtalign_aligned_structures_without_hit'
        ),
    path(
        'download/aligned_structures_reference/<slug:structure_search_job_id>/<int:result_no>/<int:hit_no>',
        views.download_aligned_reference_structure,
        name='download_gtalign_aligned_reference_structure'
        ),
    path(
        'download/aligned_structures_multiple/',
        views.download_aligned_structures_multiple,
        name='gtalign_download_aligned_structures_multiple'
        ),
]
