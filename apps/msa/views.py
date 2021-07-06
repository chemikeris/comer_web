from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404

from . import models

def submit(request):
    print('Submitting data for MSA generation using COMER results.')
    msa_job = models.save_msa_job(request.POST)
    return redirect('show_msa', msa_job.name)


def show(request, msa_job_id):
    job = get_object_or_404(models.Job, name=msa_job_id)
    finished, removed, status_msg, refresh = job.status_info()
    if finished and not removed:
        return render(
                request, 'msa/multiple_sequence_alignment.html',
                {'msa_job_id': msa_job_id}
                )
    else:
        return render(
                request, 'jobs/not_finished_or_removed.html',
                {'status_msg': status_msg, 'reload': refresh,
                    'log': job.calculation_log
                    }
                )


def download(request, msa_job_id):
    job = get_object_or_404(models.Job, name=msa_job_id)
    if job.status == job.FINISHED:
        alignment_file = job.read_results_lst()
        full_alignment_file_path = job.results_file_path(alignment_file)
        response = FileResponse(open(full_alignment_file_path, 'rb'))
        return response
    else:
        raise Http404
