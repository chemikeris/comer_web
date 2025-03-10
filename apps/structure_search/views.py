import os

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
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
    input_url = job.input_file_download_url()
    input_url_a = mark_safe(f'<a href="{input_url}">Download input</a>')
    if finished and not removed:
        summary = job.results_summary()
        context = {
            'job': job,
            'page_title': page_title,
            'results_summary': summary,
            'sequences': [r.input_description for r in summary],
            'sequence_no': None,
            'job_input': input_url_a,
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
            'job_input': input_url_a,
            'sequences': [],
            'active': 'not_finished',
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
            kwargs={'structure_search_job_id': job.name, 'result_no': result_no,}
            ),
        }
    return render(request, 'structure_search/results.html', context)


def download_input(request, job_id, result_no=None):
    job = utils.get_object_or_404_for_removed_also(models.Job, name=job_id)
    if result_no is None:
        fname = job.get_input_file(job.query_suffix())
    else:
        fname = job.input_structure_file_for_result(result_no)
    return FileResponse(open(fname, 'rb'))


def download_results(request, job_id, result_no=None):
    job = get_object_or_404(models.Job, name=job_id)
    if job.status != job.FINISHED:
        raise Http404
    if result_no is None:
        # Retrieving all results file
        results_file = job.results_file_path(job.get_output_name()+'.tar.gz')
        if os.path.isfile(results_file):
            return FileResponse(open(results_file, 'rb'))
        else:
            raise Http404
    else:
        # Retrieving JSON for a result of specific query
        results_file = job.results_file_path(
            job.read_results_lst()[result_no]['results_json']
            )
        results, json_error = utils.read_json_file(results_file)
        response = JsonResponse(results, json_dumps_params={'indent': 1})
        response['Content-Disposition'] = \
                'attachment; filename=%s_%s.json' % (job.name, result_no)
        return response

