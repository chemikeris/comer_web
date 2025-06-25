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
from apps.msa.models import StructureBasedJob as StructureMSAJob
from apps.structure_search.models import Job as StructureSearchJob
from apps.superposition.models import Superposition
from apps.superposition.models import Job as SuperpositionJob

PERMANENT_JOBS = [
    # Permanent COMER jobs:
    'benchmark2', 'benchmark3',
    # Permanent GTalign jobs:
    'benchmark13_p1', 'benchmark13_p2', 'benchmark13_p3',
    'benchmark9_p1', 'benchmark9_p2', 'benchmark9_p3',
    'example_uniref30', 'example_uniref30_raw',
    ]

class Command(BaseCommand):
    help = 'Remove old COMER web server and GTalign-web jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-example', action='store_true',
            help='Remove example job as well'
            )
        parser.add_argument(
            '--remove-job', type=str, action='store',
            help="Remove job by it's ID"
            )
        parser.add_argument(
            '--gtalign', action='store_true',
            help='Remove old GTalign-web jobs'
            )

    def handle(self, *args, **options):
        structure_search = options['gtalign']
        if options['remove_job']:
            if structure_search:
                old_jobs = []
                old_structure_jobs = StructureSearchJob.objects.filter(
                    name=options['remove_job']
                    )
            else:
                old_jobs = SearchJob.objects.filter(name=options['remove_job'])
                old_structure_jobs = []
        else:
            now = datetime.datetime.now()
            if structure_search:
                old_jobs = []
                old_structure_jobs = StructureSearchJob.objects\
                    .exclude(status=StructureSearchJob.REMOVED)\
                    .filter(date__lt=(now-datetime.timedelta(weeks=2)))
            else:
                old_jobs = SearchJob.objects\
                    .exclude(status=SearchJob.REMOVED)\
                    .filter(date__lt=(now-datetime.timedelta(weeks=13)))
                old_structure_jobs = []
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
                    really_remove = ask_if_remove_example_job()
                    if really_remove:
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
            remove_job_directories(j, calculation_server_connection)
            remove_job_itself(j)
        for j in old_structure_jobs:
            print('Removing GTalign-web job: %s (%s, %s).' % (j.job_id,
                                                              j.name,
                                                              j.date)
                )
            if j.name in PERMANENT_JOBS:
                print('Keeping permanent job %s' % j.name)
                remove_this_job = False
                continue
            elif j.name == 'gtalign_example':
                if options['remove_example']:
                    really_remove = ask_if_remove_example_job()
                    if really_remove:
                        print('Removing example job.')
                        remove_this_job = True
                    else:
                        print('Keeping example job, only MSAs are deleted.')
                        remove_this_job = False
                else:
                    print('Keeping example job, only MSAs are deleted.')
                    remove_this_job = False
                print('Removing example MSAs.')
                for m in StructureMSAJob.objects.filter(search_job=j):
                    remove_subjob(
                        m, calculation_server_connection, 'structure-based MSA'
                        )
            else:
                remove_this_job = True
            if remove_this_job:
                connection = calculation_server_connection
                superposition_subjobs = SuperpositionJob.objects.filter(
                    search_job=j
                    )
                for sj in superposition_subjobs:
                    remove_subjob(sj, connection, 'superpositon')
                msa_jobs = StructureMSAJob.objects.filter(search_job=j)
                for mj in msa_jobs:
                    remove_subjob(mj, connection, 'structure-based MSA')
                remove_job_directories(j, calculation_server_connection)
                remove_job_itself(j)
        print('Cleaning up.')
        print('Cleaning structure modeling templates from removed jobs.')
        Template.objects\
            .filter(
                search_job__in=SearchJob.objects.filter(status=SearchJob.REMOVED)
                )\
            .delete()
        print('Cleaning superpositions from removed GTalign jobs.')
        Superposition.objects\
            .filter(
                search_job__in=StructureSearchJob.objects.filter(
                    status=StructureSearchJob.REMOVED
                    )
                )\
            .delete()
        print('Cleaning e-mail addresses from removed jobs.')
        SearchJob.objects.filter(status=SearchJob.REMOVED).update(email=None)
        StructureSearchJob.objects.filter(status=StructureSearchJob.REMOVED)\
            .update(email=None)
        print('Cleaning COMER web server jobs directory.')
        for root, dirs, files in os.walk(JOBS_DIRECTORY, topdown=False):
            if not dirs and not files:
                print('Removing empty directory %s.' % root)
                os.rmdir(root)


def remove_subjob(job, connection, job_type):
    print('Removing %s job %s.' % (job_type, job.name))
    connection.remove_remote_job_directory(job.name)
    job.delete()


def remove_job_directories(job, calculation_server_connection):
    job_directory_to_remove = job.get_directory()
    try:
        print(job_directory_to_remove)
        shutil.rmtree(job_directory_to_remove)
    except FileNotFoundError:
        print('Directory %s does not exist!' % job_directory_to_remove)
    print('Removing job directory in calculation server.')
    calculation_server_connection.remove_remote_job_directory(job.name)


def remove_job_itself(job):
    if job.name in ('example', 'gtalign_example'):
        job.delete()
    else:
        job.status = job.REMOVED
        job.save()


def ask_if_remove_example_job():
    print('Do you want to remove example job?')
    answered = input()
    if answered in ('Y', 'y', 'yes'):
        return True
    else:
        return False

