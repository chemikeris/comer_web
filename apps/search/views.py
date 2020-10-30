import os
import json

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
            job_id = models.process_input_data(form.cleaned_data)
            return redirect('results', job_id=job_id)
    else:
        form = InputForm(initial=default.search_settings)
    context = {
        'form': form,
        'multiple_sequence_alignment': multiple_sequence_alignment,
        }
    return render(request, 'search/input.html', context)


def results(request, job_id):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    if job.status == job.NEW:
        finished = False
        status_msg = 'new'
    elif job.status == job.QUEUED:
        finished = False
        status_msg = 'queued'
    elif job.status == job.RUNNING:
        finished = False
        status_msg = 'running'
    elif job.status == job.FAILED:
        finished = False
        status_msg = 'failed'
    elif job.status == job.FINISHED:
        finished = True
    else:
        print('Unknown job status!')
    if finished:
        if job.number_of_sequences == 1:
            print('Single-sequence job, redirecting.')
            return redirect('detailed', job_id=job_id, sequence_no=0)

        sequences = range(job.number_of_sequences)
        return render(
                request, 'search/results_all.html',
                {'job': job, 'sequences': sequences}
                )
    else:
        return render(
                request, 'search/job_not_finished.html',
                {'status_msg': status_msg}
                )


def detailed(request, job_id, sequence_no):
    job = get_object_or_404(models.Job, name=job_id)
    print(job)
    results_file = os.path.join(
        job.get_directory(), str(sequence_no), 'results.json'
        )
    with open(results_file) as f:
        results = json.load(f)
    return render(request, 'search/results.html', {'results': results})


