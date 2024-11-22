from django.shortcuts import render


def input(request):
    "View to input GTalign query and settings"
    from .forms import StructureInputForm

    form = StructureInputForm()
    context = {
        'form': form,
        }
    return render(request, 'structure_search/input.html', context)


def results(request, job_id, redirect_to_first=False):
    pass


def detailed(request, job_id, structure_no):
    pass

