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
            redirect('gtalign_results', job_id=new_job.name)
    else:
        form = StructureInputForm()
    context = {
        'form': form,
        }
    return render(request, 'structure_search/input.html', context)


def results(request, job_id, redirect_to_first=False):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    context = {
        'job': job,
        'results_summary': job.results_summary(),
        }
    return render(request, 'structure_search/results_all.html', context)


def detailed(request, job_id, structure_no):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    print(job)
    results_file = job.results_file_path(
        job.read_results_lst()[structure_no]['results_json']
        )
    results, json_error = utils.read_json_file(results_file)
    processed_results = models.prepare_results_json(results)
    context = {
        'job': job,
        'results': processed_results,
        }
    return render(request, 'structure_search/results.html', context)

