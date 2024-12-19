from django.shortcuts import render, redirect, get_object_or_404

from . import models
from apps.core import utils


def input(request):
    "View to input GTalign query and settings"
    from .forms import StructureInputForm

    if request.method == 'POST':
        form = StructureInputForm(request.POST, request.FILES)
        if form.is_valid():
            new_job = models.process_input_data(
                form.cleaned_data, request.FILES
                )
            return redirect('gtalign_results', job_id=new_job.name)
    else:
        form = StructureInputForm()
    context = {
        'form': form,
        }
    return render(request, 'structure_search/input.html', context)


def results(request, job_id):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    finished, removed, status_msg, errors, refresh = job.status_info()
    if finished and not removed:
        summary = job.results_summary()
        context = {
            'job': job,
            'results_summary': summary,
            'sequences': [r.input_description for r in summary],
            'sequence_no': None,
            'job_options': job.read_input_file('options'),
            'active': 'summary',
            }
        return render(request, 'structure_search/results_all.html', context)
    else:
        context = {
            'job': job,
            'status_msg': status_msg,
            'reload': refresh,
            'log': job.calculation_log,
            'errors': errors,
            'job_options': job.read_input_file('options'),
            'sequences': [],
            }
        return render(request, 'jobs/not_finished_or_removed.html', context)


def detailed(request, job_id, result_no):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    print(job)
    results_file = job.results_file_path(
        job.read_results_lst()[result_no]['results_json']
        )
    results, json_error = utils.read_json_file(results_file)
    processed_results = models.prepare_results_json(results)
    context = {
        'job': job,
        'results': processed_results,
        'sequences': job.structure_headers(),
        'sequence_no': result_no,
        'active': 'detailed',
        'structure_models': None,
        'generated_msas': job.get_generated_msas().get(result_no, []),
        }
    return render(request, 'structure_search/results.html', context)

