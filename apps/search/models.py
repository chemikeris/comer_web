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
        job_directory = os.path.join(
            settings.JOBS_DIRECTORY, str(self.date), self.name
            )
        if not os.path.isdir(job_directory):
            os.makedirs(job_directory)
        self.directory = job_directory

    def __str__(self):
        s = 'COMER job\n'
        s += 'Date started: %s\n' % self.date
        s += 'Name: %s\n' % self.name
        s += 'Number of sequences: %s\n' % self.number_of_sequences
        return s


def process_input_data(input_data):
    print(input_data)
    sequences_data = input_data.pop('sequence')
    sequences = analyze_input_sequences(sequences_data)
    input_is_msa = input_data.pop('msa_input')
    job_name = generate_job_name()
    email = input_data.pop('email')
    database = input_data.pop('database')
    print(input_data)
    new_job = Job.objects.create(
        name=job_name, search_in_database=database, email=email,
        number_of_sequences=len(sequences)
        )
    print(new_job)
    save_comer_settings(
        input_data, os.path.join(new_job.directory, 'options.txt')
        )
    return new_job.name


def generate_job_name():
    job_name = ''.join(
        random.choice(string.ascii_letters+string.digits) for x in range(12)
        )
    return job_name


def analyze_input_sequences(sequences_data):
    return [sequences_data]


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

