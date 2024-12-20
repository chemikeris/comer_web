from django.core.management.base import BaseCommand, CommandError

from apps.structure_search.models import Job as StructureSearchJob
from apps.structure_search.models import read_example_structure, \
        process_input_data
from apps.structure_search.forms import StructureInputForm
from apps.structure_search import default
from apps.core.models import get_databases_for

class Command(BaseCommand):
    help = 'Create example job for GTalign-web'

    def handle(self, *args, **options):
        print('Creating example job for GTalign-web.')
        example_name = 'gtalign_example'
        example_job = StructureSearchJob.objects.filter(name=example_name)
        if example_job:
            print('Example job was already created previously!')
            return
        else:
            form_data = {}
            form_data['structure'] = read_example_structure()
            for default_setting, value in default.settings.items():
                if default_setting.startswith('pre-'):
                    s = default_setting.replace('-', '')
                else:
                    s = default_setting
                form_data[s] = value
            dbs =  get_databases_for('gtalign', 'pdb_mmcif')[0]
            form_data['database'] = dbs[0]
            form_data['email'] = ''
            form_data['description'] = 'GTalign-web example'
            form_data['input_query_files'] = None
            form = StructureInputForm(form_data)
            if form.is_valid():
                example_job = process_input_data(form_data, {}, example_name)
                print('Example job has been created.')
                print(example_job)
            else:
                print('Cannot create example job because of form errors!')
                for field, errors in form.errors.as_data().items():
                    for err in errors:
                        for e in err:
                            print('Field %s: %s' % (field, e))

