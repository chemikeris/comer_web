import os
import shutil

from django.db import models

from apps.core import utils, sequences
from apps.core.models import ComerWebServerJob, SearchSubJob, generate_job_name
from apps.search.models import Job as SearchJob


class Job(SearchSubJob, ComerWebServerJob):
    search_job = models.ForeignKey(
        SearchJob, on_delete=models.CASCADE, related_name='msa_job'
        )
    sequence_no = models.IntegerField()

    def get_output_name(self):
        return '%s__msa_out' % self.name

    def create_settings_file(self):
        directory = self.get_directory()
        parent_job_settings_file = self.search_job.get_input_file('options')
        settings_file = self.get_input_file('options')
        shutil.copy(parent_job_settings_file, settings_file)

    def create_input_data(self, template_numbers):
        directory = self.get_directory()
        search_results = self.read_search_json()
        alignments = []
        query_desc = search_results['query']['description']
        for t in template_numbers:
            hit_record = \
                search_results['search_hits'][t]['hit_record']
            a = sequences.comer_json_hit_record_to_alignment(
                query_desc, hit_record 
                )
            alignments.append(a)
        return alignments

    def read_results_lst(self):
        return self.get_output_name()+'.afa'


def save_msa_job(post_data, example=False):
    search_job = SearchJob.objects.get(name=post_data['job_id'])
    job_name = 'example_msa' if example else generate_job_name()
    sequence_no = int(post_data['sequence_no'])
    results_to_align = sorted([int(t) for t in post_data.getlist('process')])
    msa_job = Job.objects.create(
        name=job_name, search_job=search_job, sequence_no=sequence_no
        )
    initial_alignments = msa_job.create_input_data(results_to_align)
    msa_job.write_sequences(initial_alignments)
    msa_job.create_settings_file()
    return msa_job

