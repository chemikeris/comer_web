import os
import sys
import configparser
import logging
import io

import fabric

SERVER_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'settings', 'servers.ini'
    )


def read_config_file(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


class Connection:
    "Connection to server running comer-ws-backend"
    def __init__(self, server_config_file=SERVER_CONFIG_FILE):
        "Connect to Comer calculation server"
        self.config = read_config_file(server_config_file)
        if 'ssh_proxy_jump' in self.config:
            logging.info('Using proxy jump.')
            jump_connection = fabric.Connection(
                host=self.config['ssh_proxy_jump']['host'],
                port=self.config['ssh_proxy_jump']['port']
                )
        else:
            jump_connection = None
        self.connection = fabric.Connection(
                host=self.config['comer-ws-backend_server']['host'],
                gateway=jump_connection
            )

    def __del__(self):
        self.connection.close()

    def close(self):
        self.connection.close()

    def job_directory(self, job_id, create=True):
        jobs_directory = self.config['comer-ws-backend_path']['jobs_directory']
        current_job_directory = os.path.join(jobs_directory, job_id)
        if create:
            print(self.connection.run('mkdir -p %s' % current_job_directory))
        return current_job_directory
    
    def retrieve_job_file_contents(self, job_id, extension):
        job_directory = self.job_directory(job_id, create=False)
        job_file = os.path.join(job_directory, '%s.%s' % (job_id, extension))
        fd = io.BytesIO()
        self.connection.get(job_file, fd)
        file_contents = fd.getvalue().decode()
        fd.close()
        return file_contents

    def send_file(self, local_file, remote_dir):
        self.connection.put(local_file, remote_dir)

    def get_file(self, remote_file, local_dir):
        self.connection.get(remote_file, local_dir)

    def run_comer(self, job_id, job_directory):
        exe = self.config['comer-ws-backend_path']['executable']
        command = ('%s -i %s -p %s' % (exe, job_id, job_directory))
        result = self.connection.run(command)
        return result

    def check_slurm_job(self, slurm_job_no, job_id):
        try:
            squeue_result = self.connection.run(
                'squeue --noheader --long -j %s' % slurm_job_no
                )
            job_status_code = None
            if not squeue_result.stdout:
                raise
        except:
            job_status_code = self.check_job_err_file(job_id)
        job_status_log = self.check_job_status_file(job_id)
        return job_status_code, job_status_log

    def check_job_err_file(self, job_id):
        err_file_contents = self.retrieve_job_file_contents(job_id, 'err')
        err_lines = err_file_contents.splitlines()
        try:
            err_code = int(err_lines[-1])
        except ValueError:
            err_code = None
        return err_code

    def check_job_status_file(self, job_id):
        job_status_log = self.retrieve_job_file_contents(job_id, 'status')
        return job_status_log

