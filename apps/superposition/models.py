import os
import subprocess
import json
import errno
import shutil
import zipfile
import logging

from django.db import models
from django.conf import settings

from comer_web import calculation_server
from apps.core.models import ComerWebServerJob, Base3DJob, Databases, \
        generate_job_name
from apps.core.utils import read_json_file, correct_structure_file_path, \
        split_gtalign_description
from apps.structure_search.models import Job as StructureSearchJob


class Superposition(models.Model):
    search_job = models.ForeignKey(
        StructureSearchJob, on_delete=models.CASCADE,
        related_name='superposition'
        )
    result_no = models.IntegerField()
    hit_no = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['search_job', 'result_no', 'hit_no'],
                name='unique_superposition'
                ),
            ]

    def reference_file_exists(self):
        "Is there a file with superposed reference structure?"
        return self.search_job.aligned_structure_file_exists(
                self.result_no, self.hit_no
                )

    def prepare_aligned_structure(self, do_not_generate=False):
        "Prepare one aligned structure to show using web server"
        exists, result_file_path = self.reference_file_exists()
        if exists:
            # Using existing file.
            return result_file_path
        elif do_not_generate:
            raise FileNotFoundError(errno.ENOENT, str(errno.ENOENT),
                                    result_file_path)
        # It it is the first time when alignment is called, processing it.
        # Reading data.
        results_json_file = self.search_job.results_file_path(
            self.search_job.read_results_lst()[self.result_no]['results_json']
            )
        results, json_error = read_json_file(results_json_file)
        results = results['gtalign_search']
        results_lst = self.search_job.read_results_lst()
        config = calculation_server.read_config_file()
        gtalign_backend_directory = os.path.join(
            config['local_paths']['gtalign_backend'], 'bin'
            )
        print(
            'Creating GTalign aligned structures for %s, result %s, hit %s.' % \
            (self.search_job.name, self.result_no, self.hit_no)
            )
        # Preparing result structure data.
        hit_record = results['search_results'][self.hit_no]['hit_record']
        reference_description = hit_record['reference_description']
        reference_remote_dir = database_remote_directory(reference_description)
        reference_dir = config['local_paths']['structures_directory']
        reference = correct_structure_file_path(
            reference_description, reference_remote_dir, reference_dir,
            (':', '/')
            )
        # Reading transformation data.
        matrix = ','.join(map(str, hit_record['rotation_matrix_rowmajor']))
        vector = ','.join(map(str, hit_record['translation_vector']))
        aligner = os.path.join(
            gtalign_backend_directory,  'superpose1.py'
            )
        alignment_command = [
            os.path.join(settings.BASE_DIR, 'virtualenv', 'bin', 'python'),
            aligner,
            '--i2', reference['file'],
            '--c2', reference['chain'],
            '--m2', str(reference['model']),
            '-r', matrix,
            '-t', vector,
            '-o', result_file_path,
            '-2'
            ]
        subprocess.run(alignment_command)
        return result_file_path


class Job(Base3DJob, ComerWebServerJob):
    search_job = models.ForeignKey(
        StructureSearchJob, on_delete=models.CASCADE,
        related_name='superposition_job'
        )
    result_no = models.IntegerField()
    superpositions = models.ManyToManyField(Superposition)

    def query_suffix(self):
        return 'json'

    def process(self):
        return 'gtalign'

    def create_input_data(self, hit_ids):
        job_exists = self.get_job_matching_hit_ids_set(hit_ids)
        if job_exists is None:
            config = calculation_server.read_config_file()
            self.save()
            all_results = self.read_search_json()
            search_results = all_results['search_results']
            hits_to_superpose = []
            hit_records_to_superpose = []
            for hit_id in hit_ids:
                hit_id=int(hit_id)
                superposition, created = Superposition.objects.get_or_create(
                    search_job=self.search_job, result_no=self.result_no,
                    hit_no=hit_id
                    )
                if created:
                    process_this_hit = True
                else:
                    file_exists, fname = superposition.reference_file_exists()
                    if file_exists:
                        process_this_hit = False
                    else:
                        process_this_hit = True
                if process_this_hit:
                    hits_to_superpose.append(hit_id)
                    search_hit = search_results[hit_id]
                    # Changing path to file.
                    desc = search_hit['hit_record']['reference_description']
                    remote_dir = database_remote_directory(desc)
                    new_remote_dir = \
                        config['gtalign-ws-backend_path']['structures_directory']
                    new_desc_data = correct_structure_file_path(
                        desc,
                        remote_dir,
                        new_remote_dir,
                        (':', '/')
                        )
                    new_desc = '%s Chn:%s (M:%s)' % (
                        new_desc_data['file'], new_desc_data['chain'],
                        new_desc_data['model']
                        )
                    search_hit['hit_record']['reference_description'] = \
                        new_desc
                    # Saving hit data.
                    hit_records_to_superpose.append(search_hit['hit_record'])
                self.superpositions.add(superposition)
            if hits_to_superpose:
                # Writing everything to files and creating new job to process.
                out_data = []
                for hr in hit_records_to_superpose:
                    out_data.append(hr)
                self.status = self.NEW
                json_like_file = os.path.join(
                    self.get_directory(), '%s.%s' % (self.name,
                                                     self.query_suffix())
                    )
                # Writing JSON-like input for superposer
                with open(json_like_file, 'w') as f:
                    f.write('{\n')
                    f.write(' "query": ')
                    f.write(json.dumps(all_results['query'], indent=1))
                    f.write(',\n')
                    for oh in out_data:
                        f.write(' {"hit_record": {\n')
                        # reference description
                        f.write(' "reference_description": "%s",\n' % oh['reference_description'])
                        f.write(' "tfm_referenced": %s,\n' % oh['tfm_referenced'])
                        f.write(' "rotation_matrix_rowmajor": %s,\n' % oh['rotation_matrix_rowmajor'])
                        f.write(' "translation_vector": %s,\n' % oh['translation_vector'])
                        f.write('}},\n')
                    f.write('}\n')
                options_file = os.path.join(
                    self.get_directory(), '%s.options' % self.name
                    )
                with open(options_file, 'w') as f:
                    f.write('\n'.join(map(str, hits_to_superpose)))
                    f.write('\n')
            else:
                # Everything is already processed.
                self.status = self.FINISHED
                self.get_error_file(connection=None)
                self.zip_superpositions()
            return True, self
        else:
            return False, job_exists

    def get_job_matching_hit_ids_set(self, hit_ids):
        existing_superposition_jobs = Job.objects\
            .annotate(num_structures=models.Count('superpositions'))\
            .filter(
                search_job=self.search_job,
                result_no=self.result_no,
                num_structures=len(hit_ids)
                )
        ordered_hits = sorted([int(h) for h in hit_ids])
        for j in existing_superposition_jobs:
            j_superpositions = sorted(
                [s.hit_no for s in j.superpositions.all()]
                )
            if ordered_hits == j_superpositions:
                found_job = j
                break
        else:
            found_job = None
        return found_job
    
    def read_results_lst_files_line(self, files_line):
        return {'aligned_file': files_line[0]}

    def postprocess_calculation_results(self, results_files):
        options_file = os.path.join(
            self.get_directory(), '%s.options' % self.name
            )
        with open(options_file) as f:
            newly_superposed_ids = f.read().rstrip().splitlines()
        for superposed_id, rf in zip(newly_superposed_ids, results_files):
            ff, output_file = self.search_job.aligned_structure_file_exists(
                self.result_no, int(superposed_id)
                )
            rf_full_path = os.path.join(
                self.get_directory(), rf['aligned_file']
                )
            shutil.copy(rf_full_path, output_file)
        self.zip_superpositions()

    def zip_superpositions(self):
        "Create zip archive with all superpositions"
        all_superpositions_zip_file = os.path.join(
            self.get_directory(), 'superposition_%s.zip' % self.name
            )
        if os.path.isfile(all_superpositions_zip_file):
            pass
        else:
            zip_file = zipfile.ZipFile(all_superpositions_zip_file, 'w')
            for s in self.superpositions.all():
                try:
                    fname = s.prepare_aligned_structure(do_not_generate=True)
                except FileNotFoundError as err:
                    logging.error('File %s not found! Generating it.', fname)
                    fname = s.prepare_aligned_structure()
                dirname, filename = os.path.split(fname)
                zip_file.write(fname, filename)
            zip_file.close()
        return(all_superpositions_zip_file)


def save_structure_superposition_job(post_data):
    search_job = StructureSearchJob.objects.get(name=post_data['job_id'])
    result_no = int(post_data['result_no'])
    job_name = generate_job_name()
    # Creating temporary job to check if exactly the same request has been
    # already performed.
    new_superposition_job = Job(
        name=job_name, search_job=search_job, result_no=result_no
        )
    run, found_old_job = new_superposition_job.create_input_data(
        post_data.getlist('process')
        )
    if run:
        new_superposition_job.save()
        return new_superposition_job
    else:
        return found_old_job


def database_remote_directory(gtalign_result_description):
    description_parts = split_gtalign_description(gtalign_result_description)
    identifier = os.path.basename(description_parts[0])
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
    elif identifier.startswith('bfvd'):
        db_name = 'bfvd'
    else:
        db_name = 'pdb_mmcif'
    db = Databases.objects.get(program='gtalign', db=db_name)
    return db.remote_directory

