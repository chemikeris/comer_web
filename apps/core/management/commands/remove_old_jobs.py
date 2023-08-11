import os
import datetime
import shutil

from django.core.management.base import BaseCommand, CommandError

from comer_web.calculation_server import Connection
from comer_web.settings import JOBS_DIRECTORY
from apps.search.models import Job as SearchJob
from apps.model_structure.models import Job as StructureModelingJob
from apps.model_structure.models import Template
from apps.msa.models import Job as MSAJob

PERMANENT_JOBS = ['benchmark2', 'benchmark3']

class Command(BaseCommand):
    help = 'Remove old COMER web server jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-example', action='store_true',
            help='Remove example job as well'
            )
        parser.add_argument(
            '--remove-job', type=str, action='store',
            help="Remove job by it's ID"
            )

    def handle(self, *args, **options):
        if options['remove_job']:
            old_jobs = SearchJob.objects.filter(name=options['remove_job'])
        else:
            now = datetime.datetime.now()
            old_jobs = SearchJob.objects\
                .exclude(status=SearchJob.REMOVED)\
                .filter(date__lt=(now-datetime.timedelta(weeks=2)))
        calculation_server_connection = Connection()
        for j in old_jobs:
            print('Removing job: %s (%s, %s).' % (j.job_id, j.name, j.date))
            modeling_subjobs = StructureModelingJob.objects\
                .filter(search_job_id=j.job_id)\
                .exclude(name__startswith='example_model')
            for mj in modeling_subjobs:
                remove_subjob(mj, calculation_server_connection, 'modeling')
            msa_subjobs = MSAJob.objects\
                .filter(search_job_id=j.job_id)\
                .exclude(name__startswith='example_msa')
            for mj in msa_subjobs:
                remove_subjob(mj, calculation_server_connection, 'MSA')
            if j.name == 'example':
                if options['remove_example']:
                    print('Do you want to remove example job?')
                    answered = input()
                    if answered in ('Y', 'y', 'yes'):
                        print('Removing example job.')
                        connection = calculation_server_connection
                        example_modelings = StructureModelingJob.objects\
                            .filter(name__startswith='example_model')
                        for mj in example_modelings:
                            remove_subjob(mj, connection, 'modeling')
                        example_msas = MSAJob.objects\
                            .filter(name__startswith='example_msa_')
                        for mj in example_msas:
                            remove_subjob(mj, connection, 'MSA')
                    else:
                        print('Keeping example job.')
                        continue
                else:
                    print('Keeping example job, only subjobs are deleted.')
                    continue
            elif j.name in PERMANENT_JOBS:
                print('Keeping permanent job %s' % j.name)
                continue
            job_directory_to_remove = j.get_directory()
            try:
                print(job_directory_to_remove)
                shutil.rmtree(job_directory_to_remove)
            except FileNotFoundError:
                print('Directory %s does not exist!' % job_directory_to_remove)
            print('Removing job directory in calculation server.')
            calculation_server_connection.remove_remote_job_directory(j.name)
            if j.name == 'example':
                j.delete()
            else:
                j.status = j.REMOVED
                j.save()
        print('Cleaning struture modeling templates from removed jobs.')
        Template.objects\
            .filter(
                search_job__in=SearchJob.objects.filter(status=SearchJob.REMOVED)
                )\
            .delete()
        print('Cleaning e-mail addresses from removed jobs.')
        SearchJob.objects.filter(status=SearchJob.REMOVED).update(email=None)
        print('Cleaning COMER web server jobs directory.')
        for root, dirs, files in os.walk(JOBS_DIRECTORY, topdown=False):
            if not dirs and not files:
                print('Removing empty directory %s.' % root)
                os.rmdir(root)


def remove_subjob(job, connection, job_type):
    print('Removing %s job %s.' % (job_type, job.name))
    connection.remove_remote_job_directory(job.name)
    job.delete()

