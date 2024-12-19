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
    # GTalign-based MSAs
    path(
        'submit_structural_msa/',
         views.submit_structural_alignments,
         name='submit_structural_msa'
         ),
    path(
        'gtalign/show/<slug:msa_job_id>/',
        views.show,
        {'structural': True},
        name='gtalign_show_msa'
        ),
    path(
        'gtalign/download/<slug:msa_job_id>/',
        views.download,
        {'structural': True},
        name='gtalign_download_msa',
        ),
]
