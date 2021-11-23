from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from . import models

def submit_single_template_structure_model(request):
    print('Submitting data for structure modeling using single template.')
    search_job, modeling_job = models.save_structure_modeling_job(
        request.POST, False
        )
    return redirect(
            'show_modeling_job', search_job_id=search_job.name,
            modeling_job_id=modeling_job.name
            )


def submit_multiple_templates_structure_model(request):
    print('Submitting data for structure modeling using multiple templates.')
    search_job, modeling_job = models.save_structure_modeling_job(
        request.POST, True
        )
    return redirect(
            'show_modeling_job', search_job_id=search_job.name,
            modeling_job_id=modeling_job.name
            )


def show_modeling_job(request, search_job_id, modeling_job_id):
    job = get_object_or_404(models.Job, name=modeling_job_id)
    uri = request.build_absolute_uri()
    finished, removed, status_msg, errors, refresh = job.status_info()
    context = {
        'modeling_job': job,
        'errors': errors,
        'job': job.search_job,
        'sequence_no': job.sequence_no,
        'sequences': job.search_job.sequence_headers(),
        'structure_models': \
            job.search_job.get_structure_models(modeling_job_id).get(
                job.sequence_no, []
                ),
        'generated_msas': job.search_job.get_generated_msas().get(
            job.sequence_no, []
            ),
        'active': 'structure_model',
        'log': job.calculation_log,
        }
    if finished and not removed:
        return render(request, 'model_structure/modeling_job.html', context)
    else:
        not_finished_context = {'status_msg': status_msg, 'reload': refresh}
        context.update(not_finished_context)
        return render(request, 'jobs/not_finished_or_removed.html', context)


def download_model(request, modeling_job_id, model_no):
    job = get_object_or_404(models.Job, name=modeling_job_id)
    results_files = job.read_results_lst()
    model_file = job.results_file_path(results_files[model_no]['model_file'])
    with open(model_file) as f:
        pdb_file_content = f.read()
    return HttpResponse(pdb_file_content, content_type="text/plain")

