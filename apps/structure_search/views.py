from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

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
        'page_title': 'GTalign-web',
        'example_str': mark_safe(models.read_example_structure())
        }
    return render(request, 'structure_search/input.html', context)


def results(request, job_id):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    finished, removed, status_msg, errors, refresh = job.status_info()
    page_title = 'GTalign results - %s' % job.nice_name()
    if finished and not removed:
        summary = job.results_summary()
        context = {
            'job': job,
            'page_title': page_title,
            'results_summary': summary,
            'sequences': [r.input_description for r in summary],
            'sequence_no': None,
            'job_options': job.read_input_file('options'),
            'active': 'summary',
            'errors': errors,
            }
        return render(request, 'structure_search/results_all.html', context)
    else:
        context = {
            'job': job,
            'page_title': page_title,
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
    query_desc = utils.format_gtalign_description(
        results['gtalign_search']['query']['description']
        )
    page_title = 'GTalign results - %s - %s' % (job.nice_name(), query_desc)
    context = {
        'job': job,
        'page_title': page_title,
        'results': processed_results,
        'sequences': job.structure_headers(),
        'sequence_no': result_no,
        'active': 'detailed',
        'structure_models': None,
        'generated_msas': job.get_generated_msas().get(result_no, []),
        'aligned_structures_url_pattern': reverse(
            'gtalign_aligned_structures_without_hit',
            kwargs={'job_id': job.name, 'result_no': result_no,}
            ),
        }
    return render(request, 'structure_search/results.html', context)


def aligned_structures(request, job_id, result_no, hit_no):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    page_title = 'GTalign results - structure superposition'
    context = {
        'job': job,
        'page_title': page_title,
        'sequences': job.structure_headers(),
        'generated_msas': job.get_generated_msas().get(result_no, []),
        'result_no': result_no,
        'hit_no': hit_no,
        }
    return render(
            request,
            'structure_search/aligned_structures.html',
            context
            )


def download_aligned_structures(request, job_id, result_no, hit_no):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    structures_file = models.prepare_aligned_structures(job, result_no, hit_no)
    return FileResponse(open(structures_file, 'rb'))

