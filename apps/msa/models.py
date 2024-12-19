import os
import shutil

from django.db import models
from django.shortcuts import get_object_or_404

from apps.core import utils, sequences
from apps.core.models import ComerWebServerJob, SearchSubJob, generate_job_name
from apps.search.models import Job as SearchJob
from apps.structure_search.models import Job as StructureSearchJob
from apps.core.utils import format_gtalign_description

class BaseMSAJob(SearchSubJob):
    def get_output_name(self):
        return '%s__msa_out' % self.name

    def create_settings_file(self):
        directory = self.get_directory()
        parent_job_settings_file = self.search_job.get_input_file('options')
        settings_file = self.get_input_file('options')
        shutil.copy(parent_job_settings_file, settings_file)

    def create_input_data(self, template_numbers, from_gtalign=False):
        directory = self.get_directory()
        search_results = self.read_search_json()
        alignments = []
        query_desc = search_results['query']['description']
        if from_gtalign:
            query_desc = format_gtalign_description(query_desc)
        hit_desc = 'search_results' if from_gtalign else 'search_hits'
        for t in template_numbers:
            hit_record = \
                search_results[hit_desc][t]['hit_record']
            a = sequences.comer_json_hit_record_to_alignment(
                query_desc, hit_record, from_gtalign=from_gtalign 
                )
            alignments.append(a)
        return alignments

    def read_results_lst(self):
        return self.get_output_name()+'.afa'


class Job(BaseMSAJob, ComerWebServerJob):
    search_job = models.ForeignKey(
        SearchJob, on_delete=models.CASCADE, related_name='msa_job'
        )
    result_no = models.IntegerField()


class StructureBasedJob(BaseMSAJob, ComerWebServerJob):
    search_job = models.ForeignKey(
        StructureSearchJob, on_delete=models.CASCADE,
        related_name='msa_job'
        )
    result_no = models.IntegerField()


def save_msa_job(post_data, example_name=None, structural=False):
    job_name = example_name or generate_job_name()
    result_no = int(post_data['result_no'])
    results_to_align = sorted([int(t) for t in post_data.getlist('process')])
    if structural:
        search_job = StructureSearchJob.objects.get(name=post_data['job_id'])
        msa_job = StructureBasedJob.objects.create(
            name=job_name, search_job=search_job, result_no=result_no
            )
    else:
        search_job = SearchJob.objects.get(name=post_data['job_id'])
        msa_job = Job.objects.create(
            name=job_name, search_job=search_job, result_no=result_no
            )
    initial_alignments = msa_job.create_input_data(results_to_align,
                                                   from_gtalign=structural)
    msa_job.write_sequences(initial_alignments)
    msa_job.create_settings_file()
    return msa_job


def get_msa_job(msa_job_id, structural):
    if structural:
        job = get_object_or_404(StructureBasedJob, name=msa_job_id)
    else:
        job = get_object_or_404(Job, name=msa_job_id)
    return job

