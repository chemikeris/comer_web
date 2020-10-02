from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse


from . import forms
from . import default
from . import models

def input(request):
    if request.method == 'POST':
        form = forms.SequencesInputForm(request.POST)
        if form.is_valid():
            job_id = models.process_input_data(form.cleaned_data)
            return redirect('results', job_id=job_id)
    else:
        form = forms.SequencesInputForm(initial=default.search_settings)
    return render(request, 'search/input.html', {'form': form})


def results(request, job_id):
    return HttpResponse('Hello, %s' % job_id)


def detailed(request, job_id, sequence_no):
    return HttpResponse(
        'Hello, %s, showing results for %s' % (job_id, sequence_no)
        )
    

