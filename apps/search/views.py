import os
import copy

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse

from . import forms
from . import default
from . import models
from apps.core import utils

def input(request):
    "View to input query sequences or MSA"
    InputForm = forms.SequencesInputForm

    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            new_job = models.process_input_data(form.cleaned_data)
            return redirect('results', job_id=new_job.name)
    else:
        search_settings = copy.deepcopy(default.search_settings)
        form = InputForm(initial=search_settings)
    context = {
        'form': form,
        }
    return render(request, 'search/input.html', context)


def results(request, job_id):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    uri = request.build_absolute_uri()
    finished, removed, status_msg, refresh = job.status_info()
    if finished and not removed:
        if job.number_of_input_sequences == 1:
            print('Single-sequence job, redirecting.')
            return redirect('detailed', job_id=job_id, sequence_no=0)

        sequences = []
        results_files = job.read_results_lst()
        for rf in results_files:
            input_file = job.results_file_path(rf['input'])
            input_name, i_f, i_d = models.read_input_name_and_type(input_file)
            sequences.append(input_name)
        errors = job.read_error_log()
        return render(
                request, 'search/results_all.html',
                {'job': job, 'sequences': sequences, 'errors': errors}
                )
    else:
        return render(
                request, 'jobs/not_finished_or_removed.html',
                {'status_msg': status_msg, 'reload': refresh,
                    'log': job.calculation_log
                    }
                )


def detailed(request, job_id, sequence_no):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    results_files = job.read_results_lst()
    results_file = job.results_file_path(
        results_files[sequence_no]['results_json']
        )
    results = utils.read_json_file(results_file)
    if results is None:
        return render(request, 'search/error.html', {'json_error': json_error})
    input_file = job.results_file_path(results_files[sequence_no]['input'])
    input_name, input_format, input_description = \
        models.read_input_name_and_type(input_file)
    context = {
        'job': job, 'sequence_no': sequence_no,
        'results': results, 'input_name': input_name,
        'input_description': input_description,
        'input_format': '' if input_format is None else f' ({input_format})'
        }
    return render(request, 'search/results.html', context)


def show_input(request, job_id, sequence_no=None):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    if sequence_no is None:
        input_file = job.get_input_file('in')
    else:
        results_files = job.read_results_lst()
        input_file = job.results_file_path(results_files[sequence_no]['input'])
    with open(input_file) as f:
        input_data = f.read()
    return render(
            request, 'search/detailed_input.html', {'input_str': input_data}
            )
