from django.shortcuts import render, redirect, get_object_or_404

from . import models


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
    return


def detailed(request, job_id, structure_no):
    pass

