import os
import logging

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from . import models
from apps.website.models import set_and_get_session_jobs

def submit_single_template_structure_model(request):
    print('Submitting data for structure modeling using single template.')
    search_job, first_model = models.save_structure_modeling_job(
        request.POST, False
        )
    if first_model is None:
        return redirect(
                'detailed', job_id=search_job.name,
                sequence_no=request.POST['sequence_no']
                )
    else:
        return redirect(
                'show_model', search_job_id=search_job.name,
                structure_model_id=first_model.id
                )


def submit_multiple_templates_structure_model(request):
    print('Submitting data for structure modeling using multiple templates.')
    search_job, first_model = models.save_structure_modeling_job(
        request.POST, True
        )
    if first_model is None:
        return redirect(
                'detailed', job_id=search_job.name,
                sequence_no=request.POST['sequence_no']
                )
    else:
        return redirect(
                'show_model', search_job_id=search_job.name,
                structure_model_id=first_model.id
                )


def show_model(request, search_job_id, structure_model_id):
    search_job = get_object_or_404(models.SearchJob, name=search_job_id)
    structure_model = get_object_or_404(
        models.StructureModel, id=structure_model_id
        )
    sequence_no = structure_model.modeling_job.sequence_no
    finished, removed, status_msg, errors, refresh = \
        structure_model.modeling_job.status_info()
    page_title = '%s-based structure model - %s -%s' % (
        search_job.method().upper(), search_job.sequence_headers(sequence_no),
        structure_model.printable_templates_list()
        )
    context = {
        'errors': errors,
        'job': search_job,
        'page_title': page_title,
        'recent_jobs': set_and_get_session_jobs(request, search_job),
        'sequence_no': sequence_no,
        'sequences': search_job.sequence_headers(),
        'structure_models': search_job.get_structure_models(sequence_no),
        'current_structure_model': structure_model,
        'generated_msas': search_job.get_generated_msas().get(
            sequence_no, []
            ),
        'active': 'structure_model',
        'log': structure_model.modeling_job.calculation_log,
        }
    if finished and not removed:
        return render(request, 'model_structure/structure_model.html', context)
    else:
        not_finished_context = {'status_msg': status_msg, 'reload': refresh}
        context.update(not_finished_context)
        return render(request, 'jobs/not_finished_or_removed.html', context)


def download_model(request, structure_model_id, pir_file=False):
    structure_model = get_object_or_404(
        models.StructureModel, id=structure_model_id
        )
    if pir_file:
        logging.debug('Downloading PIR file.')
        file_path = structure_model.pir_file_path
    else:
        logging.debug('Downloading PDB file.')
        file_path = structure_model.file_path
    logging.debug(file_path)
    model_file = structure_model.modeling_job.results_file_path(file_path)
    with open(model_file) as f:
        pdb_file_content = f.read()
    resp = HttpResponse(pdb_file_content, content_type="text/plain")
    resp['Content-Disposition'] = 'filename=%s' % os.path.basename(model_file)
    return resp

