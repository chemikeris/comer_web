import os
import shutil

from django.db import models

from apps.core import utils, sequences
from apps.core.models import ComerWebServerJob, generate_job_name
from apps.search.models import Job as SearchJob


class Job(ComerWebServerJob):
    search_job = models.ForeignKey(
        SearchJob, on_delete=models.CASCADE, related_name='modeling_job'
        )
    sequence_no = models.IntegerField()
    number_of_templates = models.IntegerField()

    def get_directory(self):
        parent_directory = self.search_job.get_directory()
        self.directory = os.path.join(parent_directory, 'modeling', self.name)
        return self.directory

    def get_output_name(self):
        return '%s__3d_out' % self.name

    def create_settings_file(self, modeller_key, model_all_pairs):
        directory = self.get_directory()
        parent_job_settings_file = self.search_job.get_input_file('options')
        settings_file = self.get_input_file('options')
        shutil.copy(parent_job_settings_file, settings_file)
        with open(settings_file, 'a') as sf:
            sf.write('modeller_key = %s\n' % modeller_key)
            sf.write('model_all_pairs = %s\n' % int(model_all_pairs))

    def create_input_data(self, template_numbers):
        directory = self.get_directory()
        search_files = self.search_job.read_results_lst()
        search_json_file = self.search_job.results_file_path(
            search_files[self.sequence_no]['results_json']
            )
        search_results = utils.read_json_file(search_json_file)
        alignments = []
        query_desc = search_results['comer_search']['query']['description']
        for t in template_numbers:
            hit_record = \
                search_results['comer_search']['search_hits'][t]['hit_record']
            a = sequences.comer_json_hit_record_to_alignment(
                query_desc, hit_record 
                )
            alignments.append(a)
            q_starts, q_ends, t_starts, t_ends = \
                sequences.hit_alignment_starts_and_ends(
                    hit_record['alignment']
                    )
            template, created = Template.objects.get_or_create(
                search_job=self.search_job,
                sequence_no=self.sequence_no,
                result_no=t,
                query_starts=q_starts, query_ends=q_ends,
                template_starts=t_starts, template_ends=t_ends
                )
        return alignments

    def read_results_lst_files_line(self, files_line):
        "Read results lst for Comer3D job"
        rf = {}
        rf['model_file'] = files_line[0]
        rf['pir_file'] = files_line[0]
        rf['template_ids'] = files_line[-1]
        return rf


class Template(models.Model):
    search_job = models.ForeignKey(SearchJob, on_delete=models.CASCADE)
    sequence_no = models.IntegerField()
    result_no = models.IntegerField()
    query_starts = models.IntegerField()
    query_ends = models.IntegerField()
    template_starts = models.IntegerField()
    template_ends = models.IntegerField()
    modeling_job = models.ManyToManyField(Job)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['search_job', 'sequence_no', 'result_no'],
                name='unique_template'
                ),
            ]


class StructureModel(models.Model):
    modeling_job = models.ForeignKey(Job, on_delete=models.CASCADE)
    templates = models.ManyToManyField(Template)


def save_structure_modeling_job(post_data, use_multiple_templates):
    "Save data for structure modeling job"
    search_job = SearchJob.objects.get(name=post_data['job_id'])
    job_name = generate_job_name()
    sequence_no = int(post_data['sequence_no'])
    templates = sorted([int(t) for t in post_data.getlist('process')])
    modeller_key = post_data['modeller_key']
    modeling_job = Job.objects.create(
        name=job_name, search_job=search_job,
        sequence_no=sequence_no,
        number_of_templates=1
        )
    model_all_pairs = not use_multiple_templates
    modeling_job.create_settings_file(modeller_key, model_all_pairs)
    alignments = modeling_job.create_input_data(templates)
    modeling_job.write_sequences(alignments)
    return search_job, modeling_job

