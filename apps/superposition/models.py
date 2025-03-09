import os
import subprocess

from django.db import models
from django.conf import settings

from comer_web import calculation_server
from apps.core.models import ComerWebServerJob, Base3DJob, Databases, \
        generate_job_name
from apps.core.utils import read_json_file, correct_structure_file_path
from apps.structure_search.models import Job as StructureSearchJob


class Job(Base3DJob, ComerWebServerJob):
    search_job = models.ForeignKey(
        StructureSearchJob, on_delete=models.CASCADE,
        related_name='superposition_job'
        )
    result_no = models.IntegerField()
    NEW = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = 3
    possible_model_statuses = (
        (NEW, 'new'),
        (RUNNING, 'running'),
        (FINISHED, 'finished'),
        (FAILED, 'failed')
        )
    status = models.IntegerField(choices=possible_model_statuses, default=NEW)


class Superposition(models.Model):
    search_job = models.ForeignKey(
        StructureSearchJob, on_delete=models.CASCADE,
        related_name='superposition'
        )
    result_no = models.IntegerField()
    hit_no = models.IntegerField()
    jobs = models.ManyToManyField(Job)

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

    def prepare_aligned_structure(self):
        exists, result_file_path = self.reference_file_exists()
        if exists:
            # Using existing file.
            return result_file_path
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
        query_structure_fname = self\
            .search_job\
            .input_structure_file_for_result(self.result_no)
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
            '--i1', self.search_job.input_structure_file_for_result(
                self.result_no
                ),
            '--c1', 'A',
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


def save_structure_superposition_job():
    pass


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

