import os
import copy
import logging

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.core.files.uploadedfile import UploadedFile


from . import default
from comer_web import calculation_server
from comer_web.settings import BASE_URL
from apps.core.models import ComerWebServerJob, generate_job_name
from apps.core.utils import search_input_files_exist, read_json_file
from apps.core import sequences


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
        rf['profile'] = files_line[1]
        rf['msa'] = files_line[2]
        rf['input'] = files_line[3]
        try:
            rf['neff'] = files_line[4]
        except IndexError:
            rf['neff'] = None
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

    def sequence_headers(self):
        sequences = []
        results_files = self.read_results_lst()
        for rf in results_files:
            input_file = self.results_file_path(rf['input'])
            input_name, i_f, i_d = read_input_name_and_type(input_file)
            sequences.append(input_name)
        return sequences

    def results_summary(self):
        summary = []
        results_files = self.read_results_lst()
        for rf in results_files:
            summary.append(SearchResultsSummary(self, rf))
        return summary

    def results_file(self, sequence_no, what_file):
        results_files = self.read_results_lst()
        results_file = self.results_file_path(
            results_files[sequence_no][what_file]
            )
        return results_file

    def get_structure_models(self, filter_jobs_for_example=None):
        if self.name == 'example':
            example_jobs = ['example_model_1', 'example_model_2']
            if not filter_jobs_for_example is None:
                example_jobs.append(filter_jobs_for_example)
            modelings = self.modeling_job.filter(name__in=example_jobs)
        else:
            modelings = self.modeling_job.all()
        grouped_modelings = {}
        for m in modelings:
            try:
                grouped_modelings[m.sequence_no].append(m)
            except KeyError:
                grouped_modelings[m.sequence_no] = [m]
        return grouped_modelings

    def get_generated_msas(self, filter_jobs_for_example=None):
        if self.name == 'example':
            example_msa_job = 'example_msa'
            if filter_jobs_for_example is None:
                example_jobs = [example_msa_job]
            else:
                example_jobs = [example_msa_job, filter_jobs_for_example]
            msa_results = self.msa_job.filter(name__in=example_jobs)
        else:
            msa_results = self.msa_job.all()
        grouped_msas = {}
        for m in msa_results:
            try:
                grouped_msas[m.sequence_no].append(m)
            except KeyError:
                grouped_msas[m.sequence_no] = [m]
        return grouped_msas


class SearchResultsSummary:
    "Search result summary info"
    def __init__(self, job, result_files):
        rf = result_files
        input_file = job.results_file_path(rf['input'])
        i_name, i_format, i_desc = read_input_name_and_type(input_file)
        self.input_name = i_name
        self.input_format = '' if i_format is None else f' ({i_format})'
        self.input_description = i_desc
        results_json_file = job.results_file_path(rf['results_json'])
        results_json, err = read_json_file(
            results_json_file, '%s_search' % job.method()
            )
        self.results_json = results_json
        self.json_err = err
        self.number_of_results = len(results_json['search_hits'])
        self.input_length = results_json['query']['length']
        if rf['msa']:
            if rf['neff']:
                n, neff, identity = sequences.read_neff_file(
                    job.results_file_path(rf['neff'])
                    )
                self.number_of_sequences_in_msa = n
                self.msa_neff = neff
            else:
                self.number_of_sequences_in_msa = sequences.summarize_msa(
                    job.results_file_path(rf['msa'])
                    )
                self.msa_neff = None
        else:
            self.number_of_sequences_in_msa = None
            self.msa_neff = None


def process_input_data(input_data, input_files, example=False):
    "Process input sequences and settings"
    sequences_data = input_data.pop('sequence')
    input_query_f, input_parameters_f = search_input_files_exist(input_files)
    use_cother = input_data.pop('use_cother')
    job_name = 'example' if example else generate_job_name()
    email = input_data.pop('email')
    number_of_results = input_data.pop('number_of_results')
    input_data['NOHITS'] = number_of_results
    input_data['NOALNS'] = number_of_results
    new_job = Job.objects.create(
        name=job_name, email=email, is_cother_search=use_cother,
        number_of_input_sequences=len(sequences_data)
        )
    logging.info(new_job)
    options_file = new_job.get_input_file('options')
    if input_parameters_f:
        with open(options_file, 'wb') as f:
            f.write(input_parameters_f.read())
    else:
        save_comer_settings(input_data, options_file)
    new_job.write_sequences(sequences_data)
    return new_job


def save_comer_settings(settings, settings_file):
    "Save COMER search settings to a file"
    all_settings = copy.deepcopy(default.search_settings)
    for key, value in settings.items():
        if isinstance(value, list):
            writable_value = ','.join(value)
        elif isinstance(value, UploadedFile):
            continue
        elif value is None:
            continue
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
        input_format = 'fasta'
        with open(input_file) as f:
            input_name = f.readline().rstrip()[1:]
        if input_ext == '.fa':
            input_description = 'sequence'
        else:
            input_description = 'MSA'
    elif input_ext == '.a3m':
        input_format = 'A3M'
        input_description = 'MSA'
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
        input_description = 'MSA'
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

