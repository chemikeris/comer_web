import os

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

from . import default
from comer_web import calculation_server
from comer_web.settings import BASE_URL
from apps.core.models import ComerWebServerJob, generate_job_name


class Job(ComerWebServerJob):
    date = models.DateField(auto_now_add=True)
    email = models.EmailField(null=True)
    # Number of sequences is estimated after job is finished, as the sequences
    # input is parsed by calculation server.
    number_of_input_sequences = models.IntegerField()
    number_of_successful_sequences = models.IntegerField(null=True)
    is_cother_search = models.BooleanField()

    def task(self):
        app_label = self._meta.app_label
        if self.is_cother_search:
            return 'cother_'+app_label
        else:
            return app_label

    def method(self):
        if self.is_cother_search:
            return 'cother'
        else:
            return 'comer'

    def get_directory(self):
        self.directory = os.path.join(
            settings.JOBS_DIRECTORY, str(self.date), self.name
            )
        return self.directory

    def __str__(self):
        s = 'COMER job\n'
        s += 'Date started: %s\n' % self.date
        s += 'Name: %s\n' % self.name
        s += 'Number of input sequences: %s\n' % \
            self.number_of_input_sequences or '?'
        s += 'Number of results sequences: %s\n' % \
            self.number_of_successful_sequences or '?'
        s += 'Status: %s\n' % self.get_status_display()
        return s

    def get_output_name(self):
        return '%s__%s_out' % (self.name, self.method())

    def read_results_lst_files_line(self, files_line):
        "Reading results lst line for Comer search job"
        rf = {}
        rf['results_json'] = files_line[0]
        rf['input'] = files_line[-1]
        return rf

    def uri(self):
        uri = reverse('results', args=[self.name])
        return BASE_URL+uri

    def send_confirmation_email(self, status):
        if self.email:
            print('Sending confirmation email to %s.' % self.email)
            message = ''
            message += 'COMER web server job %s has %s.\n' % (self.name, status)
            message += '\n'
            message += 'To see results, please go to website:\n'
            message += self.uri()
            message += '\n'
            try:
                send_mail(
                    subject='COMER web server job %s' % self.name,
                    message=message,
                    from_email=None,
                    recipient_list=[self.email]
                    )
            except:
                print('Sending confirmation email failed.')
                import traceback
                traceback.print_exc()
            return


def process_input_data(input_data):
    "Process input sequences and settings"
    sequences_data = input_data.pop('sequence')
    use_cother = input_data.pop('use_cother')
    print(sequences_data)
    print('###########################')
    job_name = generate_job_name()
    email = input_data.pop('email')
    number_of_results = input_data.pop('number_of_results')
    input_data['NOHITS'] = number_of_results
    input_data['NOALNS'] = number_of_results
    print(input_data)
    new_job = Job.objects.create(
        name=job_name, email=email, is_cother_search=use_cother,
        number_of_input_sequences=len(sequences_data)
        )
    print(new_job)
    save_comer_settings(
        input_data, os.path.join(new_job.directory, '%s.options' % new_job.name)
        )
    new_job.write_sequences(sequences_data)
    return new_job


def save_comer_settings(settings, settings_file):
    "Save COMER search settings to a file"
    all_settings = default.search_settings
    for key, value in settings.items():
        if isinstance(value, list):
            writable_value = ','.join(value)
        else:
            writable_value = value
        all_settings[key] = writable_value
    with open(settings_file, 'w') as f:
        f.write('[OPTIONS]\n')
        for key, value in all_settings.items():
            if isinstance(value, bool):
                value = int(value)
            f.write('%s = %s' % (key, str(value)))
            f.write('\n')


def read_input_name_and_type(input_file):
    "Read input name from input file"
    input_fname, input_ext = os.path.splitext(input_file)
    if input_ext in ('.fa', '.afa'):
        input_format = 'Fasta'
        with open(input_file) as f:
            input_name = f.readline().rstrip()[1:]
        if input_ext == '.fa':
            input_description = 'sequence'
        else:
            input_description = 'multiple sequence alignment'
    elif input_ext == '.a3m':
        input_format = 'A3M'
        input_description = 'multiple sequence alignment'
        with open(input_file) as f:
            line = f.readline().strip()
            description_found = False
            while not description_found:
                if line.startswith('>'):
                    input_name = line[1:]
                    description_found = True
                else:
                    line = f.readline().strip()
    elif input_ext == '.sto':
        input_format = 'Stockholm'
        input_description = 'multiple sequence alignment'
        input_name = 'Query' + input_fname.rsplit('__', 1)[-1]
        with open(input_file) as f:
            for line in f:
                if line.startswith('#=GF DE'):
                    input_name = line.split(maxsplit=2)[-1].rstrip()
    elif input_ext in ('.pro', '.tpro'):
        input_format = None
        with open(input_file) as f:
            input_description = f.readline().strip()
            for line in f:
                if line.startswith('DESC:'):
                    input_name = line.split(':', 1)[1].strip()
    else:
        raise ValueError(
            'Input file extension should be '\
                '"fa", "afa", "a3m", "pro", "tpro" or "sto".'
            )
    return input_name, input_format, input_description

