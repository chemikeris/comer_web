import os
import zipfile
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse

from . import models

from apps.core import utils

def submit_multiple_superpositions(request):
    if request.method != 'POST':
        raise Http404
    superposition_job = models.save_structure_superposition_job(request.POST)
    return redirect(
        'gtalign_aligned_structures_multiple',
        superposition_job_id=superposition_job.name
        )
 

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


def aligned_structures_multiple(request, superposition_job_id):
    job = get_object_or_404(models.Job, name=superposition_job_id)
    finished, removed, status_msg, errors, refresh = job.status_info()
    page_title = 'GTalign results - download superposed structures'
    context = {
        'errors': errors,
        'superposition_job': job,
        'page_title': page_title,
        'job': job.search_job,
        'log': job.calculation_log,
        'sequence_no': job.result_no,
        'sequences': job.search_job.structure_headers(),
        'generated_msas': job.search_job.get_generated_msas()\
            .get(job.result_no, []),
        }
    if finished:
        return render(
                request,
                'superposition/aligned_structures_multiple.html',
                context
                )
    else:
        not_finished_context = {'status_msg': status_msg, 'reload': refresh}
        context.update(not_finished_context)
        return render(request, 'jobs/not_finished_or_removed.html', context)


def download_aligned_structures_multiple(request, superposition_job_id):
    job = utils.get_object_or_404_for_removed_also(
        models.Job, name=superposition_job_id
        )
    superposed_structures_filenames = [
        job.search_job.input_structure_file_for_result(job.result_no)
        ]
    for s in job.superpositions.all():
        try:
            fname = s.prepare_aligned_structure(do_not_generate=True)
        except FileNotFoundError as err:
            logging.error('File %s not found! Generating it.', fname)
            fname = s.prepare_aligned_structure()
        superposed_structures_filenames.append(fname)
    response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(response, 'w')
    for fname in superposed_structures_filenames:
        dirname, filename = os.path.split(fname)
        zip_file.write(fname, filename)
    zip_file.close()
    response['Content-Disposition'] = \
        'attachment; filename=superposition_%s.zip' % job.name
    return response

