import os
import string
import random
import tarfile

from django.db import models
from django.conf import settings

from . import default
from comer_web import calculation_server


class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=140, unique=True)
    email = models.EmailField(null=True)
    # Number of sequences is estimated after job is finished, as the sequences
    # input is parsed by calculation server.
    number_of_sequences = models.IntegerField(null=True)
    search_in_database = models.CharField(max_length=20)
    # Possible job status. Jobs are new by default.
    NEW = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3
    FAILED = 4
    REMOVED = 5
    possible_job_statuses = (
        (NEW, 'new'),
        (QUEUED, 'queued'),
        (RUNNING, 'running'),
        (FINISHED, 'finished'),
        (FAILED, 'failed'),
        (REMOVED, 'removed')
        )
    status = models.IntegerField(
        choices=possible_job_statuses, default=NEW
        )
    slurm_job_no = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create job directory.
        self.get_directory()
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

    def get_directory(self):
        self.directory = os.path.join(
            settings.JOBS_DIRECTORY, str(self.date), self.name
            )
        return self.directory

    def __str__(self):
        s = 'COMER job\n'
        s += 'Date started: %s\n' % self.date
        s += 'Name: %s\n' % self.name
        s += 'Number of sequences: %s\n' % self.number_of_sequences or '?'
        s += 'Status: %s\n' % self.get_status_display()
        return s

    def get_input_file(self, what_file):
        self.get_directory()
        fname = os.path.join(self.directory, '%s.%s' % (self.name, what_file))
        return fname
    
    def get_output_name(self):
        return '%s__comer_out' % self.name

    def submit_to_calculation(self):
        "Submit COMER job for calculation to calculation server"
        connection = calculation_server.Connection()
        remote_job_directory = connection.job_directory(self.name, create=True)
        connection.send_file(self.get_input_file('options'), remote_job_directory)
        connection.send_file(self.get_input_file('in'), remote_job_directory)
        run_result = connection.run_comer(self.name, remote_job_directory)
        job_calculation_slurm_id = run_result.stdout
        print(job_calculation_slurm_id)
        self.status = self.QUEUED
        self.slurm_job_no = int(job_calculation_slurm_id)
        self.save(update_fields=['status', 'slurm_job_no'])
        connection.close()

    def check_status(self):
        connection = calculation_server.Connection()
        job_status_code, job_status_log = connection.check_slurm_job(
            self.slurm_job_no, self.name
            )
        if job_status_code is None:
            pass
            # This means that job status will not be changed in DB.
        elif job_status_code == 0:
            self.status = getattr(self, 'FINISHED')
            self.get_results_files(connection)
            results_files = self.read_results_lst()
            self.number_of_sequences = len(results_files)
        elif job_status_code == 1:
            self.status = getattr(self, 'FAILED')
        else:
            raise ValueError(
                'Unknown COMER job status code: %s' % job_status_code
                )
        self.save()
        connection.close()
        return job_status_log

    def get_results_files(self, connection=None):
        "Retrieve results files from calculation server"
        if connection is None:
            connection = calculation_server.Connection()
        # Getting remote archive.
        archive_filename = self.get_output_name() + '.tar.gz'
        remote_directory = connection.job_directory(self.name, create=False)
        remote_results_archive = os.path.join(remote_directory, archive_filename)
        local_directory = self.get_directory()
        local_results_archive = os.path.join(local_directory, archive_filename)
        connection.get_file(remote_results_archive, local_results_archive)
        # Extracting results files.
        tar = tarfile.open(local_results_archive, 'r')
        tar.extractall(local_directory)

    def read_results_lst(self):
        "Read results.lst file and retrieve list of results.json files"
        results_lst_file = os.path.join(
            self.get_directory(), self.get_output_name()+'.lst'
            )
        results_files = []
        with open(results_lst_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                else:
                    # Taking first element and unquoting it.
                    rf = line.split()[0].rstrip('"').lstrip('"')
                    results_files.append(rf)
        return results_files


def process_input_data(input_data):
    input_is_msa = input_data.pop('msa_input')
    sequences_data, seq_format = input_data.pop('sequence')
    print(seq_format)
    print(sequences_data)
    print('###########################')
    job_name = generate_job_name()
    email = input_data.pop('email')
    number_of_results = input_data.pop('number_of_results')
    input_data['NOHITS'] = number_of_results
    input_data['NOALNS'] = number_of_results
    print(input_data)
    new_job = Job.objects.create(
        name=job_name, search_in_database='', email=email
        )
    print(new_job)
    save_comer_settings(
        input_data, os.path.join(new_job.directory, '%s.options' % new_job.name)
        )
    write_sequence(sequences_data, seq_format, new_job.directory, new_job.name)
    return new_job


def generate_job_name():
    job_name = ''.join(
        random.choice(string.ascii_letters+string.digits) for x in range(12)
        )
    return job_name


def save_comer_settings(settings, settings_file):
    "Save COMER search settings to a file"
    all_settings = default.search_settings
    for key, value in settings.items():
        all_settings[key] = value
    with open(settings_file, 'w') as f:
        for key, value in all_settings.items():
            if isinstance(value, bool):
                value = int(value)
            f.write('%s = %s' % (key, str(value)))
            f.write('\n')


def write_sequence(
        sequence_data, seq_format, where_to_write, job_name
        ):
    "Write input sequence or alignment to files"
    output_file = os.path.join(where_to_write, '%s.%s' % (job_name, 'in'))
    with open(output_file, 'w') as f:
        f.write(sequence_data)



