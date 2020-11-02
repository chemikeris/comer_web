import os
import string
import random

from django.db import models
from django.conf import settings

from . import default

class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=140, unique=True)
    email = models.EmailField(null=True)
    number_of_sequences = models.IntegerField()
    search_in_database = models.CharField(max_length=20)
    # Possible job status. Jobs are new by default.
    NEW = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3
    FAILED = 4
    possible_job_statuses = (
        (NEW, 'new'),
        (QUEUED, 'queued'),
        (RUNNING, 'running'),
        (FINISHED, 'finished'),
        (FAILED, 'failed'),
        )
    status = models.IntegerField(
        choices=possible_job_statuses, default=NEW
        )

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
        s += 'Number of sequences: %s\n' % self.number_of_sequences
        s += 'Status: %s\n' % self.get_status_display()
        return s


def process_input_data(input_data):
    input_is_msa = input_data.pop('msa_input')
    sequences_data, seq_format = input_data.pop('sequence')
    print(seq_format)
    print(sequences_data)
    print('###########################')
    job_name = generate_job_name()
    email = input_data.pop('email')
    database = input_data.pop('database')
    number_of_results = input_data.pop('number_of_results')
    input_data['NOHITS'] = number_of_results
    input_data['NOALNS'] = number_of_results
    print(input_data)
    new_job = Job.objects.create(
        name=job_name, search_in_database=database, email=email,
        number_of_sequences=len(sequences_data)
        )
    print(new_job)
    save_comer_settings(
        input_data, os.path.join(new_job.directory, 'options.txt')
        )
    write_sequence(sequences_data, seq_format, new_job.directory, input_is_msa)
    return new_job.name


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
        sequence_data, seq_format, where_to_write, multiple_sequence_alignment
        ):
    "Write input sequence or alignment to files"
    if seq_format == 'plain':
        extension = 'txt'
    elif seq_format == 'fasta':
        if multiple_sequence_alignment:
            extension = 'afa'
        else:
            extension = 'fasta'
    elif seq_format == 'stockholm':
        extension = 'sto'
    else:
        raise ValueError('Unknown sequence format given: %s.' % seq_format)

    output_file = os.path.join(where_to_write, '%s.%s' % ('input', extension))
    with open(output_file, 'w') as f:
        f.write(sequence_data)

