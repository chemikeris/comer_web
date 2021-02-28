from django.shortcuts import render, redirect, get_object_or_404

from comer_web.models import track_status
from . import models

def submit(request):
    print('Submitting data for MSA generation using COMER results.')
    msa_job = models.save_msa_job(request.POST)
    return redirect('show_msa', msa_job.name)


def show(request, msa_job_id):
    job = get_object_or_404(models.Job, name=msa_job_id)
    uri = request.build_absolute_uri()
    finished, removed, status_msg, job_log, refresh = track_status(job, uri)
    if finished and not removed:
        alignment_file = job.read_results_lst()
        full_alignment_file_path = job.results_file_path(alignment_file)
        with open(full_alignment_file_path) as f:
            alignment = f.read()
        return render(
                request, 'msa/multiple_sequence_alignment.html',
                {'msa_str': alignment}
                )
    else:
        return render(
                request, 'jobs/not_finished_or_removed.html',
                {'status_msg': status_msg, 'reload': refresh, 'log': job_log}
                )
