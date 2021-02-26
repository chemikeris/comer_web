from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from comer_web.models import generate_job_name, track_status
from apps.search.models import Job as SearchJob
from . import models

def submit_single_template_structure_model(request):
    print('Submitting data for structure modeling.')
    print(request.POST)
    search_job = SearchJob.objects.get(name=request.POST['job_id'])
    job_name = generate_job_name()
    sequence_no = int(request.POST['sequence_no'])
    templates = sorted([int(t) for t in request.POST.getlist('process')])
    modeller_key = request.POST['modeller_key']
    modeling_job = models.Job.objects.create(
        name=job_name, search_job=search_job,
        sequence_no=sequence_no,
        number_of_templates=1
        )
    modeling_job.create_settings_file(modeller_key, True)
    alignments = modeling_job.create_input_data(templates)
    modeling_job.write_sequences(alignments)
    return redirect(
            'show_modeling_job', search_job_id=search_job.name,
            modeling_job_id=modeling_job.name
            )


def submit_multiple_templates_structure_model(request):
    modeling_job.create_settings_file(request.POST['modeller_key'], False)
    return redirect(
            'show_modeling_job', search_job_id=search_job.name,
            modeling_job_id=modeling_job.name
            )


def show_modeling_job(request, search_job_id, modeling_job_id):
    job = get_object_or_404(models.Job, name=modeling_job_id)
    uri = request.build_absolute_uri()
    finished, removed, status_msg, job_log, refresh = track_status(job, uri)
    if finished and not removed:
        results_files = job.read_results_lst()
        errors = job.read_error_log()
        context = {
            'templates': [r['template_ids'] for r in results_files],
            'job': job
            }
        return render(
                request, 'model_structure/modeling_job.html', context
                )
    else:
        return render(
                request, 'jobs/not_finished_or_removed.html',
                {'status_msg': status_msg, 'reload': refresh, 'log': job_log}
                )


def show_model(request, modeling_job_id, model_no):
    job = get_object_or_404(models.Job, name=modeling_job_id)
    results_files = job.read_results_lst()
    model_file = job.results_file_path(results_files[model_no]['model_file'])
    with open(model_file) as f:
        pdb_file_content = f.read()
    return HttpResponse(pdb_file_content, content_type="text/plain")

