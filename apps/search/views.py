from django.shortcuts import render, redirect
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
    return HttpResponse('Hello, %s' % job_id)


def detailed(request, job_id, sequence_no):
    return HttpResponse(
        'Hello, %s, showing results for %s' % (job_id, sequence_no)
        )
    

