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
        'show_model/<slug:search_job_id>/<int:structure_model_id>',
        views.show_model,
        name='show_model'
        ),
    path(
        'download_model/<slug:structure_model_id>',
        views.download_model,
        name='model_structure_download_model'
        ),
]
