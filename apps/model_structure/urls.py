from django.urls import path

from . import views

urlpatterns = [
    path(
        'submit_single/',
        views.submit_single_template_structure_model,
        name='submit_single_template_structure_model'
        ),
    path(
        'submit_multiple/',
        views.submit_multiple_templates_structure_model,
        name='submit_multiple_templates_structure_model'
        ),
    path(
        'show_modeling_job/<slug:search_job_id>/<slug:modeling_job_id>',
        views.show_modeling_job,
        name='show_modeling_job'
        ),
    path(
        'download_model/<slug:modeling_job_id>/<int:model_no>',
        views.download_model,
        name='model_structure_download_model'
        ),
]
