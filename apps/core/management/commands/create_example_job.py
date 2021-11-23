import os
import copy
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict

from apps.search.models import Job as SearchJob
from apps.search.models import process_input_data
from apps.search.forms import SequencesInputForm
from apps.search import default
from apps.model_structure.models import save_structure_modeling_job
from apps.msa.models import save_msa_job


class Command(BaseCommand):
    help = 'Create example job for COMER web server'

    def handle(self, *args, **kwargs):
        print('Creating example search job.')
        example_job = SearchJob.objects.filter(name='example')
        if example_job:
            print('Example job was already created previously!')
            example_job = example_job[0]
        else:
            fasta_file = os.path.join(settings.BASE_DIR, 'doc', 'example.fasta')
            with open(fasta_file) as f:
                fasta_str = f.read()
            form_data = copy.deepcopy(default.search_settings)
            form_data['sequence'] = fasta_str
            form_data['multi_sequence_fasta'] = True
            form_data['use_cother'] = False
            form_data['comer_db'] = [settings.COMER_DATABASES[0][0]]
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
        print('Creating example structure modeling job.')
        try:
            example_modeling_1 = example_job.modeling_job.get(
                name='example_model_1'
                )
            example_modeling_2 = example_job.modeling_job.get(
                name='example_model_2'
                )
            print('Structure modeling example was already created previously!')
        except ObjectDoesNotExist:
            if not finished(example_job):
                print(
                    'Search failed, cannot create structure modeling example.'
                    )
                return
            simulated_post_data = QueryDict(
                'job_id=%s&sequence_no=0&process=0&process=2&modeller_key=' % \
                    example_job.name
                )
            sj, modeling_example_1 = save_structure_modeling_job(
                    simulated_post_data, False, 'example_model_1'
                    )
            sj, modeling_example_2 = save_structure_modeling_job(
                    simulated_post_data, False, 'example_model_2'
                    )
            print('Structure modeling examples have been created.')
        print('Creating MSA job example.')
        try:
            msa_example_job = example_job.msa_job.get(name='example_msa')
            print('MSA example was already created previously!')
        except ObjectDoesNotExist:
            if not finished(example_job):
                print('Search failed, cannot create MSA example.')
                return
            sequences_for_msa = range(20)
            simulated_post_str = 'job_id=%s&sequence_no=0' % example_job.name
            for s in sequences_for_msa:
                simulated_post_str += '&process=%s' % s
            simulated_post_data = QueryDict(simulated_post_str)
            save_msa_job(simulated_post_data, example=True)
            print('Example MSA job has been created.')


def finished(job):
    if job.status == job.FAILED:
        return False
    else:
        while not job.status == job.FINISHED:
            time.sleep(10)
        return True

