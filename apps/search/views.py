import os
import json
import copy

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse

from . import forms
from . import default
from . import models

def input(request, multiple_sequence_alignment=False):
    "View to input query sequences or MSA"
    if multiple_sequence_alignment:
        InputForm = forms.MultipleAlignmentInputForm
    else:
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
        'multiple_sequence_alignment': multiple_sequence_alignment,
        }
    return render(request, 'search/input.html', context)


def results(request, job_id):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    removed = False
    job_log = None
    refresh = False
    if job.status == job.NEW:
        finished = False
        status_msg = 'new'
        # Submitting new job to calculation server.
        job.submit_to_calculation()
        refresh = True
    elif job.status == job.QUEUED:
        finished = False
        status_msg = 'queued'
        # Checking job status.
        job_log = job.check_status()
        refresh = True
    elif job.status == job.RUNNING:
        finished = False
        status_msg = 'running'
        job_log = job.check_status()
        refresh = True
    elif job.status == job.FAILED:
        finished = False
        status_msg = 'failed'
    elif job.status == job.FINISHED:
        finished = True
    elif job.status == job.REMOVED:
        finished = True
        removed = True
        status_msg = 'removed'
        refresh = False
    else:
        print('Unknown job status!')
    if finished and not removed:
        if job.number_of_sequences == 1:
            print('Single-sequence job, redirecting.')
            return redirect('detailed', job_id=job_id, sequence_no=0)

        sequences = []
        results_files = job.read_results_lst()
        for rf in results_files:
            input_file = job.results_file_path(rf['input'])
            input_name = models.read_input_name(input_file)
            sequences.append(input_name)
        errors = job.read_error_log()
        return render(
                request, 'search/results_all.html',
                {'job': job, 'sequences': sequences, 'errors': errors}
                )
    else:
        return render(
                request, 'search/job_not_finished_or_removed.html',
                {'status_msg': status_msg, 'reload': refresh, 'log': job_log}
                )


def detailed(request, job_id, sequence_no):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    results_files = job.read_results_lst()
    results_file = job.results_file_path(
        results_files[sequence_no]['results_json']
        )
    with open(results_file) as f:
        results = json.load(f)
    return render(request, 'search/results.html', {'results': results})


