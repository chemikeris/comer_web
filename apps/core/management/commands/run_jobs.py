import sys
import time
import logging

from django.core.management.base import BaseCommand, CommandError

from apps.search import models as search_models
from apps.model_structure import models as structure_models
from apps.msa import models as msa_models
from comer_web import calculation_server


class Command(BaseCommand):
    help = 'Manage COMER web server jobs'

    def handle(self, **options):
        print('Starting job dispatcher for COMER web server.')
        while True:
            try:
                track_jobs()
                time.sleep(10)
            except KeyboardInterrupt:
                sys.exit(0)


def retrieve_unfinished_jobs(job_model):
    jobs = job_model.objects.\
        exclude(status=job_model.FINISHED).\
        exclude(status=job_model.FAILED).\
        exclude(status=job_model.REMOVED)
    return jobs


def track_jobs():
    search_jobs = retrieve_unfinished_jobs(search_models.Job)
    modeling_jobs = retrieve_unfinished_jobs(structure_models.Job)
    msa_jobs = retrieve_unfinished_jobs(msa_models.Job)
    all_jobs = list(search_jobs) + list(modeling_jobs) + list(msa_jobs)
    if all_jobs:
        connection = calculation_server.Connection()
    for j in all_jobs:
        track_status(j, connection)


def track_status(job, connection):
    finished = False
    removed = False
    status_msg = None
    job_log = None
    refresh = False
    if job.status == job.NEW:
        status_msg = 'new'
        # Submitting new job to calculation server.
        try:
            job.submit_to_calculation(connection)
        except Exception as e:
            logging.error(e)
            job.status = job.FAILED
            job.save()
        refresh = True
    elif job.status == job.QUEUED:
        status_msg = 'queued'
        # Checking job status.
        job.calculation_log = job.check_calculation_status(connection)
        if job.calculation_log:
            if job.calculation_log.strip().endswith('Queued.'):
                pass
            else:
                job.status = job.RUNNING
        job.save()
        refresh = True
    elif job.status == job.RUNNING:
        status_msg = 'running'
        job.calculation_log = job.check_calculation_status(connection)
        job.save()
        refresh = True
    else:
        print('Unknown job status!')

