from django.shortcuts import render
from django.http import FileResponse, Http404

from . import models

from apps.core import utils

def aligned_structures(request, structure_search_job_id, result_no, hit_no):
    job = utils.get_object_or_404_for_removed_also(
        models.StructureSearchJob, name=structure_search_job_id
        )
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
            'superposition/aligned_structures.html',
            context
            )


def download_aligned_reference_structure(
        request, structure_search_job_id, result_no, hit_no
        ):
    job = utils.get_object_or_404_for_removed_also(
        models.StructureSearchJob, name=structure_search_job_id
        )
    superposition, created = models.Superposition.objects.get_or_create(
        search_job=job, result_no=result_no, hit_no=hit_no
        )
    structure_file = superposition.prepare_aligned_structure()
    return FileResponse(open(structure_file, 'rb'))


def download_aligned_structures_multiple(request):
    raise Http404
    if request.method != 'POST':
        raise Http404
    job = utils.get_object_or_404_for_removed_also(
        models.Job, name=request.POST['job_id']
        )
    result_no = int(request.POST['result_no'])
    hits = sorted([int(t) for t in request.POST.getlist('process')])
    superposed_structures_filenames = [
        models.prepare_aligned_structure(job, result_no, None)
        ]
    for h in hits:
        fname = models.prepare_aligned_structure(job, result_no, h)
        superposed_structures_filenames.append(fname)
    response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(response, 'w')
    for fname in superposed_structures_filenames:
        dirname, filename = os.path.split(fname)
        zip_file.write(fname, filename)
    zip_file.close()
    response['Content-Disposition'] = 'attachment; filename=superposition.zip'
    return response

