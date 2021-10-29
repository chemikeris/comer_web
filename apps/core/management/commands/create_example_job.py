import os
import copy

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.search.models import Job as SearchJob
from apps.search.models import process_input_data
from apps.search.forms import SequencesInputForm
from apps.search import default


class Command(BaseCommand):
    help = 'Create example job for COMER web server'

    def handle(self, *args, **kwargs):
        example_job_exists = SearchJob.objects.filter(name='example')
        if example_job_exists:
            print('Example job was already created previously!')
            return
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



