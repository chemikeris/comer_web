from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404

from . import models
from apps.website.models import set_and_get_session_jobs

def submit(request):
    print('Submitting data for MSA generation using COMER results.')
    msa_job = models.save_msa_job(request.POST)
    return redirect('show_msa', msa_job.name)


def submit_structural_alignments(request):
    print('Submitting data for MSA generation using GTalign results.')
    msa_job = models.save_msa_job(request.POST, structural=True)
    return redirect('gtalign_show_msa', msa_job.name)


def show(request, msa_job_id, structural=False):
    job = models.get_msa_job(msa_job_id, structural)
    finished, removed, status_msg, errors, refresh = job.status_info()
    if structural:
        title = 'GTalign'
    else:
        title = job.search_job.method().upper()
    page_title = '%s-based multiple sequence alignment' % title
    if structural:
        session_jobs = []
        result_headers = job.search_job.structure_headers(),
        structure_models = []
    else:
        session_jobs = set_and_get_session_jobs(request, job.search_job)
        result_headers = job.search_job.sequence_headers()
        structure_models = job.search_job.get_structure_models(job.result_no)
    context = {
        'msa_job_id': msa_job_id,
        'page_title': page_title,
        'errors': errors,
        'job': job.search_job,
        'recent_jobs': session_jobs,
        'sequence_no': job.result_no,
        'sequences': result_headers,
        'structure_models': structure_models,
        'generated_msas': job.search_job.get_generated_msas(msa_job_id).\
                get(job.result_no, []),
        'active': 'msa',
        'log': job.calculation_log,
        }
    if finished and not removed:
        return render(request, 'msa/multiple_sequence_alignment.html', context)
    else:
        not_finished_context = {'status_msg': status_msg, 'reload': refresh}
        context.update(not_finished_context)
        return render(request, 'jobs/not_finished_or_removed.html', context)


def download(request, msa_job_id, structural=False):
    job = models.get_msa_job(msa_job_id, structural)
    if job.status == job.FINISHED:
        alignment_file = job.read_results_lst()
        full_alignment_file_path = job.results_file_path(alignment_file)
        response = FileResponse(open(full_alignment_file_path, 'rb'))
        return response
    else:
        raise Http404

