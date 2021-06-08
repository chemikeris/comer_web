import os
import datetime
import shutil

from django.core.management.base import BaseCommand, CommandError

from comer_web.settings import JOBS_DIRECTORY
from apps.search.models import Job as SearchJob
from apps.model_structure.models import Job as StructureModelingJob
from apps.msa.models import Job as MSAJob

class Command(BaseCommand):
    help = 'Remove old COMER web server jobs'

    def handle(self, *args, **options):
        print('Removing old COMER web server search jobs.')
        now = datetime.datetime.now()
        old_jobs = SearchJob.objects.exclude(status=SearchJob.REMOVED).filter(
            date__lt=(now-datetime.timedelta(weeks=2))
            )
        for j in old_jobs:
            print('Removing job: %s (%s, %s).' % (j.job_id, j.name, j.date))
            StructureModelingJob.objects.filter(search_job_id=j.job_id).delete()
            MSAJob.objects.filter(search_job_id=j.job_id).delete()
            job_directory_to_remove = j.get_directory()
            try:
                print(job_directory_to_remove)
                shutil.rmtree(job_directory_to_remove)
            except FileNotFoundError:
                print('Directory %s does not exist!' % job_directory_to_remove)
            j.status = j.REMOVED
            j.save()
        print('Cleaning COMER web server jobs directory.')
        for root, dirs, files in os.walk(JOBS_DIRECTORY, topdown=False):
            if not dirs and not files:
                print('Removing empty directory %s.' % root)
                os.rmdir(root)

