import os
import random
import string
import tarfile
import csv

from django.db import models

from comer_web import calculation_server

class ComerWebServerJob(models.Model):
    class Meta:
        abstract = True

    job_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=140, unique=True)
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
    calculation_log = models.TextField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create job directory.
        self.get_directory()
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

    def get_directory(self):
        raise NotImplementedError

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

    def submit_to_calculation(self, connection):
        "Submit COMER job for calculation to calculation server"
        remote_job_directory = connection.job_directory(self.name, create=True)
        connection.send_file(self.get_input_file('options'), remote_job_directory)
        connection.send_file(self.get_input_file('in'), remote_job_directory)
        run_result = connection.run_comer(
            self.name, remote_job_directory, self._meta.app_label
            )
        job_calculation_slurm_id = run_result.stdout
        print(job_calculation_slurm_id)
        self.status = self.QUEUED
        self.slurm_job_no = int(job_calculation_slurm_id)
        self.save(update_fields=['status', 'slurm_job_no'])

    def check_calculation_status(self, connection):
        uri = None
        job_status_code, job_status_log = connection.check_slurm_job(
            self.slurm_job_no, self.name
            )
        if job_status_code is None:
            pass
            # This means that job status will not be changed in DB.
        elif job_status_code == 0:
            self.get_results_files(connection)
            results_files = self.read_results_lst()
            self.number_of_successful_sequences = len(results_files)
            self.status = getattr(self, 'FINISHED')
            self.send_confirmation_email('finished')
        elif job_status_code == 1:
            self.status = getattr(self, 'FAILED')
            self.send_confirmation_email('failed')
        else:
            raise ValueError(
                'Unknown COMER job status code: %s' % job_status_code
                )
        self.save()
        return job_status_log

    def get_results_files(self, connection):
        "Retrieve results files from calculation server"
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
    
    def read_error_log(self):
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

    def send_confirmation_email(self, *args, **kwargs):
        pass

    def uri(self):
        raise NotImplementedError

    def status_info(self):
        finished = False
        removed = False
        status_msg = None
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
        elif self.status == self.FINISHED:
            status_msg = 'finished'
            finished = True
        elif self.status == self.REMOVED:
            status_msg = 'removed'
            finished = True
            removed = True
        else:
            print('Unknown job status!')
        return finished, removed, status_msg, refresh


def generate_job_name():
    "Generate job name having 12 random alphanumeric symbols"
    job_name = ''.join(
        random.choice(string.ascii_letters+string.digits) for x in range(12)
        )
    return job_name

