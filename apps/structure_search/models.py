import os
import shutil
import logging
import tarfile
import glob

from django.db import models

from apps.core.models import SearchJob, generate_job_name


class Job(SearchJob):
    "GTalign search job"
    def method(self):
        return 'gtalign'

    def query_suffix(self):
        return 'tar'

    def process(self):
        return 'gtalign'

    def write_sequences(self):
        logging.error('Structure search job cannot write sequences!')

    def read_results_lst_files_line(self, files_line):
        "Reading results lst line for GTalign search job"
        rf = {}
        rf['results_json'] = files_line[0]
        rf['structure_description'] = files_line[1]
        rf['structure_length'] = files_line[2]
        return rf


def process_input_data(input_data, input_files):
    "Process input data for GTalign search"
    structure_str = input_data.pop('structure')
    email = input_data.pop('email')
    description = input_data.pop('description')
    database = input_data.pop('database')
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
    save_gtalign_settings(new_job.get_input_file('options'), database)
    return new_job


def save_gtalign_settings(settings_file, database):
    default_settings_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'default_settings.txt')
    shutil.copy(default_settings_file, settings_file)
    with open(settings_file, 'a') as f:
        f.write('gtalign_db = %s' % database)
       
