import os
import shutil
import logging
import tarfile
import glob
import subprocess

from django.db import models
from django.conf import settings

from apps.core.models import SearchJob, generate_job_name, Databases
from apps.core.utils import read_json_file, format_gtalign_description
from comer_web import calculation_server

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

    def summarize_results_for_query(self, results_files):
        return StructureSearchResultsSummary(self, results_files)

    def structure_headers(self):
        structures = []
        results_files = self.read_results_lst()
        for i, rf in enumerate(results_files):
            s = self.summarize_results_for_query(rf)
            structures.append(s.input_description)
        return structures

    def aligned_structures_subdirectory(self):
        aligned_structures_subdirectory = os.path.join(
            self.get_directory(), 'aligned_structures'
            )
        if not os.path.isdir(aligned_structures_subdirectory):
            os.makedirs(aligned_structures_subdirectory)
        return aligned_structures_subdirectory


class StructureSearchResultsSummary:
    def __init__(self, job, results_data):
        r = results_data
        input_structure_data = r['structure_description'].split()
        structure_file = input_structure_data[0]
        self.structure_file = structure_file.split(':')[-1]
        chain_desc = input_structure_data[1]
        self.chain = chain_desc.split(':')[-1]
        try:
            model_desc = input_structure_data[2]
            self.model = model_desc.lstrip('(').rstrip(')').split(':')[-1]
        except IndexError:
            self.model = 1
        self.input_description = '%s Chain:%s M:%s' % (
            self.structure_file, self.chain, self.model)
        self.input_length = r['structure_length']
        json_file = job.results_file_path(r['results_json'])
        results_json, err = read_json_file(json_file, job.method()+'_search')
        self.number_of_results = len(results_json['search_results'])


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


def prepare_results_json(results_json):
    "Remove unnecessary data from GTalign results JSON"
    res = results_json['gtalign_search']
    for i, hit_record in enumerate(res['search_results']):
        hr = hit_record['hit_record']
        description = format_gtalign_description(hr['reference_description'])
        hr['reference_description'] = description
        res['search_summary'][i]['summary_entry']['description'] = description
    return results_json


def prepare_aligned_structures(job, result_no, hit_no):
    result_file_path = os.path.join(
        job.aligned_structures_subdirectory(),
        '%s_%s_%s.pdb' % (job.name, result_no, hit_no)
        )
    # Using already prepared file, if it exists.
    if os.path.isfile(result_file_path):
        logging.info('Using already aligned structure file %s',
                     result_file_path)
        return result_file_path
    print(
        'Creating GTalign aligned structures for %s, result %s, hit %s.' % \
        (job.name, result_no, hit_no)
        )
    # It it is the first time when alignment is called, processing it.
    # Reading data.
    results_file = job.results_file_path(
        job.read_results_lst()[result_no]['results_json']
        )
    results, json_error = read_json_file(results_file)
    results = results['gtalign_search']
    hit_record = results['search_results'][hit_no]['hit_record']
    config = calculation_server.read_config_file()
    # Preparing query structure data.
    query_structure_description = results['query']['description']
    query_remote_dir = config['comer-ws-backend_path']['jobs_directory']
    query_dir = job.get_directory()
    query = structure_data(
        query_structure_description, query_remote_dir, query_dir+'/',
        ('%s.tar:' % job.name, 'input/')
        )
    # Preparing result structure data.
    reference_description = hit_record['reference_description']
    reference_remote_dir = database_remote_directory(reference_description)
    reference_dir = config['local_paths']['structures_directory']
    reference = structure_data(
        reference_description, reference_remote_dir, reference_dir,
        (':', '/')
        )
    # Reading transformation data.
    matrix = ','.join(map(str, hit_record['rotation_matrix_rowmajor']))
    vector = ','.join(map(str, hit_record['translation_vector']))
    aligner = os.path.join(
        config['local_paths']['gtalign_backend'], 'bin', 'superpose1.py'
        )
    alignment_command = [
        os.path.join(settings.BASE_DIR, 'virtualenv', 'bin', 'python'),
        aligner,
        '--i1', query['file'],
        '--c1', query['chain'],
        '--m1', str(query['model']),
        '--i2', reference['file'],
        '--c2', reference['chain'],
        '--m2', str(reference['model']),
        '-r', matrix,
        '-t', vector,
        '-o', result_file_path,
        '-2',
        ]
    subprocess.run(alignment_command)
    return result_file_path


def structure_data(description, old_dir, new_dir, tar_replacement=None):
    parts = description.split()
    remote_path = parts[0]
    chain = parts[1].split(':')[1]
    try:
        model = parts[2][1:-1].split(':')[1]
    except IndexError:
        model = 1
    local_path = remote_path.replace(old_dir, new_dir)
    if tar_replacement:
        local_path = local_path.replace(tar_replacement[0], tar_replacement[1])
    output = {'file': local_path, 'chain': chain, 'model': model}
    return output


def database_remote_directory(gtalign_structure_result_file):
    identifier = os.path.basename(gtalign_structure_result_file)
    if identifier.startswith('ecod'):
        db_name = 'ecod'
    elif identifier.startswith('scope'):
        db_name = 'scop'
    elif identifier.startswith('swissprot'):
        db_name = 'swissprot'
    elif identifier.startswith('uniref'):
        db_name = 'uniref30'
    elif identifier.startswith('UP'):
        db_name = 'proteomes'
    else:
        db_name = 'pdb_mmcif'
    db = Databases.objects.get(program='gtalign', db=db_name)
    return db.remote_directory
        
