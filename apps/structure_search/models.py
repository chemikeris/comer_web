import sys
import os
import shutil
import logging
import tarfile
import glob
import subprocess

from Bio import PDB

from django.db import models
from django.conf import settings
from django.urls import reverse

from apps.core.models import SearchJob, generate_job_name, Databases
from apps.core.utils import read_json_file, format_gtalign_description, \
        correct_structure_file_path, split_gtalign_description
from comer_web import calculation_server

class Job(SearchJob):
    "GTalign search job"
    def method(self):
        return 'gtalign'

    def server(self):
        return 'GTalign-web'

    def query_suffix(self):
        return 'tar'

    def process(self):
        return 'gtalign'

    def uri(self):
        uri = reverse('gtalign_results', args=[self.name])
        return settings.BASE_URL+uri

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

    def aligned_structure_file_exists(self, result_no, hit_no=None):
        if hit_no is None:
            # Input structure is necessary, that is selected from input file
            # according to model number and chain name.
            aligned_file_name = '%s_input_%s.pdb' % (self.name, result_no)
        else:
            results_json_file = self.results_file_path(
                self.read_results_lst()[result_no]['results_json']
                )
            results, json_err = read_json_file(results_json_file)
            results = results['gtalign_search']['search_results']
            hit_record = results[hit_no]['hit_record']
            description = format_gtalign_description(
                hit_record['reference_description']
                )
            description = description.split()[0]
            aligned_file_name = '%s_%s_%s.pdb' % (self.name,
                                                  result_no,
                                                  description)
        result_file_path = os.path.join(
            self.aligned_structures_subdirectory(), aligned_file_name
            )
        if os.path.isfile(result_file_path):
            logging.info('Using already aligned structure file %s',
                         result_file_path)
            return True, result_file_path
        else:
            return False, result_file_path

    def input_file_download_url(self):
        return reverse('gtalign_download_input', args=[self.name])

    def input_structure_file_for_result(self, result_no):
        "Generate name of file with input structure (exact model and chain)"
        exists, result_file_path = self.aligned_structure_file_exists(result_no)
        if exists:
            return result_file_path
        # Reading config file
        config = calculation_server.read_config_file()
        results_lst = self.read_results_lst()
        # Preparing query structure data.
        query_structure_description = results_lst[result_no]['structure_description']
        query_remote_dir = config['comer-ws-backend_path']['jobs_directory']
        query_dir = self.get_directory()
        # Path to query file is sometimes truncated in the query structure
        # description, this needs to be corrected.
        if query_structure_description.startswith('...'):
            fname_and_suffix = os.path.basename(query_structure_description)
            query_structure_description = os.path.join(
                query_remote_dir, self.name, fname_and_suffix
                )
        query = correct_structure_file_path(
            query_structure_description, query_remote_dir, query_dir+'/',
            ('%s.tar:' % self.name, 'input/')
        )
        print(
            'Creating GTalign query structure file for %s, result %s.' % \
                (self.name, result_no)
            )
        # Using code from calculation backend module.
        try:
            from superpose1 import GetStructureModelChain
        except ImportError:
            gtalign_backend_directory = os.path.join(
                config['local_paths']['gtalign_backend'], 'bin'
                )
            sys.path.append(gtalign_backend_directory)
            from superpose1 import GetStructureModelChain
        code, chain1, header1 = GetStructureModelChain(
            [query['file']], query['chain'], int(query['model'])
            )
        chain1.id = 'A'
        builder = PDB.StructureBuilder.StructureBuilder()
        builder.init_structure('Sup')
        builder.init_model(0,0)
        outstr = builder.get_structure()
        chain1.id = 'A'
        outstr[0].add(chain1)
        io = PDB.PDBIO()
        io.set_structure(outstr)
        io.save(result_file_path)
        return result_file_path


class StructureSearchResultsSummary:
    def __init__(self, job, results_data):
        r = results_data
        input_structure_data = split_gtalign_description(
            r['structure_description']
            )
        structure_file = input_structure_data[0]
        self.structure_file = structure_file.split(':')[-1]
        self.chain = input_structure_data[1]
        self.model = input_structure_data[2]
        self.input_description = '%s Chain:%s M:%s' % (
            self.structure_file, self.chain, self.model)
        self.input_length = r['structure_length']
        json_file = job.results_file_path(r['results_json'])
        results_json, err = read_json_file(json_file, job.method()+'_search')
        self.number_of_results = len(results_json['search_results'])


def process_input_data(input_data, input_files, example=False):
    "Process input data for GTalign search"
    structure_str = input_data.pop('structure')
    email = input_data.pop('email')
    description = input_data.pop('description')
    database = input_data.pop('database')
    try:
        input_query_files = input_files.getlist('input_query_files')
    except (KeyError, AttributeError):
        input_query_files = []
    del input_data['input_query_files']
    job_name = example or generate_job_name()
    new_job = Job.objects.create(
        name=job_name, email=email, description=description
        )
    # Writing input files.
    input_directory = os.path.join(new_job.get_directory(), job_name, 'input')
    os.makedirs(input_directory)
    if structure_str:
        structure_str = structure_str.lstrip()
        if structure_str.startswith('data_'):
            extension = '.cif'
        elif structure_str.startswith('#'):
            input_lines = structure_str.splitlines()
            format_found = False
            parsing = False
            line, input_lines = input_lines[0], input_lines[1:]
            while not format_found and input_lines:
                if line.startswith('#'):
                    line, input_lines = input_lines[0], input_lines[1:]
                    continue
                else:
                    if line.startswith('data_'):
                        extension = '.cif'
                    else:
                        extension = '.pdb'
                    format_found = True
            if not format_found:
                extension = '.pdb'
        else:
            extension = '.pdb'
        fname = os.path.join(input_directory, job_name+extension)
        with open(fname, 'w') as f:
            f.write(structure_str)
    for query_file in input_query_files:
        if tarfile.is_tarfile(query_file):
            tar = tarfile.open(fileobj=query_file)
            tar.extractall(input_directory)
        else:
            fname = os.path.join(input_directory, query_file.name)
            with open(fname, 'wb') as f:
                f.write(query_file.read())
    input_archive_file = os.path.join(new_job.get_directory(), job_name+'.tar')
    with tarfile.open(input_archive_file, 'w') as tf:
        for fname in os.listdir(input_directory):
            tf.add(os.path.join(input_directory, fname), arcname=fname)
    save_gtalign_settings(
        new_job.get_input_file('options'), database, input_data
        )
    return new_job


def save_gtalign_settings(settings_file, database, input_settings):
    default_settings_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'default_settings.txt')
    shutil.copy(default_settings_file, settings_file)
    with open(settings_file, 'a') as f:
        for setting, value in input_settings.items():
            if setting.startswith('pre'):
                s = setting.replace('pre', 'pre-')
            elif setting == 'nhits':
                s = setting
                f.write(f'--nalns={value}\n')
            elif setting == 'nogaps':
                s = 'no-deletions'
            else:
                s = setting
            if isinstance(value, bool):
                if value:
                    f.write(f'--{s}\n')
            else:
                f.write(f'--{s}={value}\n')
        f.write('gtalign_db = %s\n' % database)


def parse_gtalign_job_options(options_file_contents):
    options = {}
    for line in options_file_contents.splitlines():
        opt = line.rstrip().split('=')
        if len(opt) == 1:
            options[opt[0]] = True
        else:
            key = opt[0].strip()
            value = opt[1].strip()
            options[key] = value
    return options


def prepare_results_json(results_json):
    "Remove unnecessary and add additional data from GTalign results JSON"
    res = results_json['gtalign_search']
    for i, hit_record in enumerate(res['search_results']):
        hr = hit_record['hit_record']
        description, annotation = format_gtalign_description(
            hr['reference_description'], get_annotation=True
            )
        hr['reference_description'] = description
        hr['reference_annotation'] = annotation
        res['search_summary'][i]['summary_entry']['description'] = description
    return results_json


def read_example_structure():
    example_structure_fname = '7wwv_A.pdb'
    example_structure_file = os.path.join(
        settings.BASE_DIR, 'doc', example_structure_fname
        )
    with open(example_structure_file) as f:
        return f.read()

