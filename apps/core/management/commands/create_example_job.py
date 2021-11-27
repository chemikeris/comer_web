import os
import copy
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict

from apps.core.sequences import read_example_queries
from apps.search.models import Job as SearchJob
from apps.search.models import process_input_data
from apps.search.forms import SequencesInputForm
from apps.search import default
from apps.model_structure.models import save_structure_modeling_job
from apps.msa.models import save_msa_job


class Command(BaseCommand):
    help = 'Create example job for COMER web server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-subjobs', action='store_true',
            help='Skip creating structure modeling and MSA jobs'
            )

    def handle(self, *args, **options):
        print('Creating example search job.')
        example_job = SearchJob.objects.filter(name='example')
        if example_job:
            print('Example job was already created previously!')
            example_job = example_job[0]
        else:
            example_str = read_example_queries()
            form_data = copy.deepcopy(default.search_settings)
            form_data['sequence'] = example_str
            form_data['multi_sequence_fasta'] = True
            form_data['use_cother'] = False
            form_data['comer_db'] = [
                settings.COMER_DATABASES[0][0],
                settings.COMER_DATABASES[-1][0],
                ]
            form_data['cother_db'] = [settings.COTHER_DATABASES[0][0]]
            form_data['hhsuite_db'] = settings.HHSUITE_DATABASES[0][0]
            form_data['sequence_db'] = settings.SEQUENCE_DATABASES[0][0]
            form_data['number_of_results'] = default.number_of_results
            form = SequencesInputForm(form_data)
            if form.is_valid():
                example_job = process_input_data(form.cleaned_data, {}, True)
                print('Example job has been created.')
                print(example_job)
            else:
                print('Cannot create example job because of form errors!')
                for field, errors in form.errors.as_data().items():
                    for err in errors:
                        for e in err:
                            print('Field %s: %s' % (field, e))
        if options['skip_subjobs']:
            print('Skipping structure modeling and MSA examples.')
            return
        print('Creating example structure modeling job.')
        modelings = {
            'example_model_1': [0, range(6), False],
            'example_model_2': [0, range(6), True],
            'example_model_3': [2, [1], False],
            'example_model_4': [3, range(12), False],
            'example_model_5': [3, range(2), True],
            }
        try:
            for modeling_job_name in modelings.keys():
                example_modeling = example_job.modeling_job.get(
                    name=modeling_job_name
                    )
            print('Structure modeling example was already created previously!')
        except ObjectDoesNotExist:
            if not finished(example_job):
                print(
                    'Search failed, cannot create structure modeling example.'
                    )
                return
            for modeling_example_name, example_data in modelings.items():
                sequence_no, numbers, multi_structure = example_data
                simulated_post_str = \
                    'job_id=%s&sequence_no=%s&&modeller_key=' % \
                    (example_job.name, sequence_no)
                post_data = simulate_post_data(simulated_post_str, numbers)
                save_structure_modeling_job(
                    post_data, multi_structure, modeling_example_name
                    )
            print('Structure modeling examples have been created.')
        print('Creating MSA job example.')
        msa_data = {
            'example_msa_1': [0, range(20)],
            'example_msa_2': [1, range(22)],
            'example_msa_3': [2, range(10)],
            'example_msa_4': [3, range(78)],
            }
        try:
            for msa_job_name in msa_data.keys():
                msa_example_job = example_job.msa_job.get(name=msa_job_name)
            print('MSA example was already created previously!')
        except ObjectDoesNotExist:
            if not finished(example_job):
                print('Search failed, cannot create MSA example.')
                return
            for example_msa_name, example_data in msa_data.items():
                sequence_no, sequences_for_msa = example_data
                simulated_post_str = 'job_id=%s&sequence_no=%s' % \
                    (example_job.name, sequence_no)
                simulated_post_data = simulate_post_data(
                    simulated_post_str, sequences_for_msa
                    )
                save_msa_job(simulated_post_data, example_msa_name)
            print('Example MSA job has been created.')


def finished(job):
    if job.status == job.FAILED:
        return False
    else:
        i = 0
        while not job.status == job.FINISHED:
            print('Search job still running for %s s.' % (i*10))
            i += 1
            time.sleep(10)
            job.refresh_from_db()
        return True


def simulate_post_data(starting_post_data, sequence_numbers):
    post_data = starting_post_data
    for s in sequence_numbers:
        post_data += '&process=%s' % s
    return QueryDict(post_data)

