import os
import shutil
import logging
import tarfile
import glob

from django.db import models

from apps.core.models import SearchJob, generate_job_name


class Job(SearchJob):
    # Number of structures and number of successful structures are idenfitied
    # after the job is finished in calculation server.
    number_of_input_structures = models.IntegerField(null=True)
    number_of_successful_structures = models.IntegerField(null=True)

    def method(self):
        return 'gtalign'

    def write_sequences(self):
        logging.error('Structure search job cannot write sequences!')


def process_input_data(input_data, input_files):
    "Process input data for GTalign search"
    structure_str = input_data.pop('structure')
    email=input_data.pop('email')
    description=input_data.pop('description')
    try:
        input_query_files = input_files.getlist('input_query_files')
    except KeyError:
        input_query_files = []
    job_name = generate_job_name()
    new_job = Job.objects.create(
        name=job_name, email=email, description=description
        )
    # Writing input files.
    input_directory = os.path.join(new_job.get_directory(), job_name, 'input')
    os.makedirs(input_directory)
    if structure_str:
        fname = os.path.join(input_directory, job_name)
        with open(fname, 'w') as f:
            f.write(structure_str)
    for query_file in input_query_files:
        fname = os.path.join(input_directory, query_file.name)
        with open(fname, 'wb') as f:
            f.write(query_file.read())
    input_archive_file = os.path.join(new_job.get_directory(), job_name+'.tar')
    with tarfile.open(input_archive_file, 'w') as tf:
        for fname in os.listdir(input_directory):
            tf.add(os.path.join(input_directory, fname), arcname=fname)
    save_gtalign_settings(new_job.get_input_file('settings'))
    return new_job


def save_gtalign_settings(settings_file):
    default_settings_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'default_settings.txt')
    shutil.copy(default_settings_file, settings_file)
       
