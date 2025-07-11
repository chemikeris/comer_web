import os
import random
import string
import tarfile
import csv

from django.db import models
from django.db.utils import OperationalError
from django.conf import settings
from django.core.mail import send_mail

from . import utils

class ComerWebServerJob(models.Model):
    class Meta:
        abstract = True

    job_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=140, unique=True)
    description = models.CharField(max_length=140, null=True)
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
    status = models.IntegerField(choices=possible_job_statuses, default=NEW)
    slurm_job_no = models.IntegerField(null=True)
    calculation_log = models.TextField(null=True)
    error_log = models.TextField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create job directory.
        self.get_directory()
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

    def get_directory(self):
        raise NotImplementedError

    def nice_name(self):
        if self.description:
            return self.description
        else:
            return self.name

    def get_output_name(self):
        raise NotImplementedError

    def write_sequences(self, sequence_data):
        "Write input sequence or alignment to files"
        output_file = os.path.join(
            self.get_directory(), '%s.%s' % (self.name, 'in')
            )
        with open(output_file, 'w') as f:
            f.write('\n//\n'.join(sequence_data))
            f.write('\n//\n')

    def task(self):
        return self._meta.app_label

    def method(self):
        raise NotImplementedError

    def server(self):
        raise NotImplementedError

    def query_suffix(self):
        return 'in'

    def process(self):
        return 'comer'

    def submit_to_calculation(self, connection):
        "Submit COMER job for calculation to calculation server"
        remote_job_directory = connection.job_directory(self.name, create=True)
        connection.send_file(
            self.get_input_file('options'), remote_job_directory
            )
        connection.send_file(
            self.get_input_file(self.query_suffix()),
            remote_job_directory
            )
        run_result = connection.run_computation(
            self.name, remote_job_directory, self.process(), self.task()
            )
        job_calculation_slurm_id = run_result.stdout
        print(job_calculation_slurm_id)
        self.status = self.QUEUED
        self.slurm_job_no = int(job_calculation_slurm_id)
        self.save(update_fields=['status', 'slurm_job_no'])

    def check_calculation_status(self, connection):
        "Check job calculation status and process results if it has finished"
        job_status_code, job_status_log = connection.check_slurm_job(
            self.slurm_job_no, self.name
            )
        if job_status_code is None:
            pass
            # This means that job status will not be changed in DB.
        elif job_status_code == 0:
            self.get_results_files(connection)
            results_files = self.read_results_lst()
            self.number_of_successful_queries = len(results_files)
            self.postprocess_calculation_results(results_files)
            self.status = getattr(self, 'FINISHED')
            self.send_confirmation_email('finished')
        elif job_status_code == 1:
            self.status = getattr(self, 'FAILED')
            self.get_error_file(connection)
            self.postprocess_failed_calculation()
            self.send_confirmation_email('failed')
        else:
            raise ValueError(
                'Unknown COMER job status code: %s' % job_status_code
                )
        self.save()
        return job_status_log

    def postprocess_calculation_results(self, *args, **kwargs):
        "Postprocess calculation results, if necessary"
        pass

    def postprocess_failed_calculation(self, *args, **kwargs):
        "Postprocess failed calculation, if necessary"
        pass

    def get_results_files(self, connection):
        "Retrieve results files from calculation server"
        # Getting remote archive.
        archive_filename = self.get_output_name() + '.tar.gz'
        local_directory = self.get_directory()
        local_results_archive = self.get_remote_file(
            connection, archive_filename
            )
        # Extracting results files.
        tar = tarfile.open(local_results_archive, 'r')
        tar.extractall(local_directory)

    def get_error_file(self, connection):
        "Retrieve error file for failed job"
        error_filename = self.name + '.err'
        if connection is None:
            local_error_file = os.path.join(
                self.get_directory(), error_filename
                )
            open(local_error_file, 'w').close()
            return
        local_error_file = self.get_remote_file(connection, error_filename)
        # Truncating two last lines which provide error code.
        with open(local_error_file, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            for l in lines[:-2]:
                f.write(l)
            f.truncate()

    def get_remote_file(self, connection, fname):
        "Retrieve job file from calculation server"
        remote_directory = connection.job_directory(self.name, create=False)
        remote_file = os.path.join(remote_directory, fname)
        local_directory = self.get_directory()
        local_file = os.path.join(local_directory, fname)
        connection.get_file(remote_file, local_file)
        return local_file

    def read_error_log_file(self):
        "Read job error log"
        err_file = self.results_file_path(self.name+'.err')
        with open(err_file) as f:
            errors = f.read().strip()
        return errors

    def results_file_path(self, results_file):
        results_file = os.path.join(self.get_directory(), results_file)
        return results_file

    def read_results_lst(self):
        "Read results.lst file and retrieve list of results files"
        results_lst_file = self.results_file_path(self.get_output_name()+'.lst')
        results_files = []
        with open(results_lst_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                else:
                    # Taking first and last elements and unquoting them.
                    files = list(
                        csv.reader([line], delimiter='\t', quotechar='"')
                        )[0]
                    rf = self.read_results_lst_files_line(files)
                    results_files.append(rf)
        return results_files

    def read_results_lst_files_line(self, *args, **kwargs):
        raise NotImplementedError

    def get_input_file(self, what_file):
        self.get_directory()
        fname = os.path.join(self.directory, '%s.%s' % (self.name, what_file))
        return fname

    def read_input_file(self, what_file):
        with open(self.get_input_file(what_file)) as f:
            return f.read()

    def send_confirmation_email(self, *args, **kwargs):
        pass

    def uri(self):
        raise NotImplementedError

    def status_info(self):
        finished = False
        removed = False
        status_msg = None
        errors = None
        refresh = False
        if self.status == self.NEW:
            status_msg = 'new'
            refresh = True
        elif self.status == self.QUEUED:
            status_msg = 'queued'
            refresh = True
        elif self.status == self.RUNNING:
            status_msg = 'running'
            refresh = True
        elif self.status == self.FAILED:
            status_msg = 'failed'
            try:
                errors = self.read_error_log_file()
            except FileNotFoundError:
                errors = 'Error log not found for a failed job!'
            else:
                if not errors:
                    try:
                        errors = self.calculation_log.split('\n\n')[-1]
                    except IndexError:
                        errors = ''
        elif self.status == self.FINISHED:
            status_msg = 'finished'
            finished = True
            errors = self.read_error_log_file()
        elif self.status == self.REMOVED:
            status_msg = 'removed'
            finished = True
            removed = True
        else:
            print('Unknown job status!')
        return finished, removed, status_msg, errors, refresh

    def results_summary(self):
        raise NotImplementedError


class SearchJob(ComerWebServerJob):
    class Meta:
        abstract = True

    date = models.DateField(auto_now_add=True)
    email = models.EmailField(null=True)
    number_of_input_queries = models.IntegerField(null=True)
    number_of_successful_queries = models.IntegerField(null=True)

    def server(self):
        raise NotImplementedError

    def get_directory(self):
        self.directory = os.path.join(
            settings.JOBS_DIRECTORY, str(self.date), self.name
            )
        return self.directory

    def get_output_name(self):
        return '%s__%s_out' % (self.name, self.method())

    def __str__(self):
        s = '%s job\n' % self.method().upper()
        s += 'Date started: %s\n' % self.date
        s += 'Name: %s\n' % self.name
        s += 'Number of input queries: %s\n' % \
            self.number_of_input_queries or '?'
        s += 'Number of results queries: %s\n' % \
            self.number_of_successful_queries or '?'
        s += 'Status: %s\n' % self.get_status_display()
        return s

    def results_summary(self):
        summary = []
        results_files = self.read_results_lst()
        for rf in results_files:
            summary.append(self.summarize_results_for_query(rf))
        return summary

    def get_generated_msas(self, filter_jobs_for_example=None):
        if self.name == 'example':
            example_jobs = ['example_msa_%s' % i for i in range(1,5)]
            if not filter_jobs_for_example is None:
                example_jobs.append(filter_jobs_for_example)
            msa_results = self.msa_job.filter(name__in=example_jobs)
        else:
            msa_results = self.msa_job.all()
        grouped_msas = {}
        for m in msa_results:
            try:
                grouped_msas[m.result_no].append(m)
            except KeyError:
                grouped_msas[m.result_no] = [m]
        return grouped_msas

    def send_confirmation_email(self, status):
        if self.email:
            print('Sending confirmation email to %s.' % self.email)
            message = ''
            message += '%s search job "%s" has %s.\n' % (
                self.server(), self.nice_name(), status
                )
            message += '\n'
            message += 'To see the results, please go to website:\n'
            message += self.uri()
            message += '\n'
            try:
                send_mail(
                    subject='%s job "%s"' % (self.server(), self.nice_name()),
                    message=message,
                    from_email=None,
                    recipient_list=[self.email]
                    )
            except:
                print('Sending confirmation email failed.')
                import traceback
                traceback.print_exc()
            return


class SearchSubJob:
    "Class for defining common methods for jobs derived from SearchJob"
    def get_directory(self):
        parent_directory = self.search_job.get_directory()
        self.directory = os.path.join(
            parent_directory, self.task() , self.name
            )
        return self.directory

    def read_search_json(self):
        search_files = self.search_job.read_results_lst()
        search_json_file = self.search_job.results_file_path(
            search_files[self.result_no]['results_json']
            )
        search_results, unused_json_err = utils.read_json_file(
            search_json_file, filter_key='%s_search' % self.search_job.method()
            )
        return search_results

    def create_input_data(self, *args, **kwargs):
        raise NotImplementedError


class Base3DJob(SearchSubJob):
    "Base class for common methods related to 3D structure jobs"
    def get_output_name(self):
        return '%s__3d_out' % self.name


class Databases(models.Model):
    "COMER web server databases"
    class Program(models.TextChoices):
        COMER = 'comer', 'COMER'
        COTHER = 'cother', 'COTHER'
        HHsuite = 'hhsuite', 'HH-suite'
        hmmer = 'hmmer', 'hmmer'
        GTalign = 'gtalign', 'GTalign'
    program = models.CharField(
        max_length=160, choices=Program.choices
        )
    class DB(models.TextChoices):
        pdb = 'pdb', 'PDB70'
        uniref30 = 'uniref30', 'UniRef30'
        uniref50 = 'uniref50', 'UniRef50'
        scop = 'scop', 'SCOPe70'
        pfam = 'pfam', 'Pfam'
        mgy = 'mgy', 'MGnify_clusters'
        swissprot = 'swissprot', 'UniProtKB/SwissProt90'
        ecod = 'ecod', 'ECOD-F70'
        cog = 'cog', 'COG-KOG'
        ncbicd = 'ncbicd', 'NCBI-Conserved-Domains'
        bfd = 'bfd', 'BFD'
        pdb_mmcif = 'pdb_mmcif', 'PDB mmCIF'

    db = models.CharField(
        max_length=160, choices=DB.choices
        )
    calculation_server_description = models.CharField(max_length=160)
    version = models.CharField(max_length=160, null=True)
    remote_directory = models.CharField(max_length=255, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['program', 'db'],
                name='unique_program_database'
                ),
            ]

    def __str__(self):
        if self.version:
            return '%s_%s' % (self.get_db_display(), self.version)
        else:
            return self.get_db_display()

    def get_db_display_gtalign(self):
        if self.db == 'pdb_mmcif':
            return 'PDB mmCIF'
        elif self.db == 'scop':
            return 'SCOPe40'
        elif self.db == 'ecod':
            return 'ECOD_F70'
        elif self.db == 'swissprot':
            return 'UniProtKB/SwissProt'
        elif self.db == 'uniref30':
            return 'UniRef30'
        elif self.db == 'proteomes':
            return 'UniProt Reference Proteomes'
        elif self.db == 'pdb_scop_ecod':
            return 'PDB mmCIF|SCOPe40|ECOD_F70'
        elif self.db == 'pdb_scop_ecod_sw_prot':
            return 'PDB mmCIF|SCOPe40|ECOD_F70|SwissProt|Reference Proteomes'
        elif self.db == 'bfvd':
            return 'BFVD (viral proteins)'
        else:
            raise ValueError('Unknown database name: %s' % self.db)


def get_databases_for(program, db=None):
    try:
        databases = Databases.objects\
            .filter(program=program).order_by('pk').all()
        if db:
            # db should be a list of database names
            databases = databases.filter(db__in=db)
        descriptions = []
        for d in databases:
            if program == 'gtalign':
                desc = d.get_db_display_gtalign()
            else:
                desc = str(d)
            descriptions.append([d.calculation_server_description, desc])
    except OperationalError:
        descriptions = []
    return descriptions


def generate_job_name():
    "Generate job name having 12 random alphanumeric symbols"
    job_name = ''.join(
        random.choice(string.ascii_letters+string.digits) for x in range(12)
        )
    return job_name

