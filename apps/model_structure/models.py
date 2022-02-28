import os
import shutil
import logging

from django.db import models

from apps.core import utils, sequences
from apps.core.models import ComerWebServerJob, SearchSubJob, generate_job_name
from apps.search.models import Job as SearchJob


MAX_TEMPLATES_IN_ONE_MODEL = 7


class Job(SearchSubJob, ComerWebServerJob):
    search_job = models.ForeignKey(
        SearchJob, on_delete=models.CASCADE, related_name='modeling_job'
        )
    sequence_no = models.IntegerField()
    number_of_templates = models.IntegerField()

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

    def create_input_data(
            self, template_numbers, model_all_pairs, modeller_key):
        search_results = self.read_search_json()
        query_desc = search_results['query']['description']
        alignments = []
        templates = []
        for t in template_numbers:
            hit_record = \
                search_results['search_hits'][t]['hit_record']
            template_name = hit_record['target_description'].split()[0]
            if utils.is_Pfam_result(template_name):
                continue # Pfam entries have no structures yet, skipping them.
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
                template_name=utils.standard_result_name(template_name),
                result_no=t,
                query_starts=q_starts, query_ends=q_ends,
                template_starts=t_starts, template_ends=t_ends
                )
            templates.append(template)
        if not templates:
            do_modeling = False
            first_model = None
            return do_modeling, first_model
        if model_all_pairs:
            new_alignments = []
            new_templates = []
            for template, alignment in zip(templates, alignments):
                found_model = self.get_model_matching_template_set([template])
                if not found_model:
                    new_templates.append(template)
                    new_alignments.append(alignment)
                elif found_model.status == found_model.FAILED:
                    print('Re-doing failed modeling using %s.' % template)
                    self.save()
                    found_model.redo(new_modeling_job=self)
                    new_alignments.append(alignment)
            if new_templates or new_alignments:
                do_modeling = True
                self.save()
                self.write_sequences(new_alignments)
                self.create_settings_file(modeller_key, model_all_pairs)
                for t in new_templates:
                    sm = StructureModel.objects.create(modeling_job=self)
                    sm.templates.add(t)
            else:
                print('No new template sets found, all models are done.')
                do_modeling = False
            first_model = StructureModel.objects.filter(templates=templates[0])[0]
        else:
            # Creating one model based on first MAX_TEMPLATES_IN_ONE_MODEL
            # templates, unless such a model has been already generated
            # previously.
            usable_alignments = alignments[:MAX_TEMPLATES_IN_ONE_MODEL]
            usable_templates = templates[:MAX_TEMPLATES_IN_ONE_MODEL]
            found_same_model = self.get_model_matching_template_set(
                usable_templates
                )
            if found_same_model is None:
                do_modeling = True
                self.save()
                self.write_sequences(usable_alignments)
                self.create_settings_file(modeller_key, model_all_pairs)
                sm = StructureModel.objects.create(modeling_job=self)
                for t in usable_templates:
                    sm.templates.add(t)
                first_model = sm
            elif found_same_model.status == found_same_model.FAILED:
                print('Re-doing failed multi-template model.')
                do_modeling = True
                self.save()
                found_same_model.redo(new_modeling_job=self)
                self.write_sequences(usable_alignments)
                self.create_settings_file(modeller_key, model_all_pairs)
                first_model = found_same_model
            else:
                print('Found exactly the same model, skipping modeling.')
                first_model = found_same_model
                do_modeling = False
        return do_modeling, first_model

    def read_results_lst_files_line(self, files_line):
        "Read results lst for Comer3D job"
        rf = {}
        rf['model_file'] = files_line[0]
        rf['pir_file'] = files_line[0]
        rf['template_ids'] = files_line[-1]
        return rf

    def postprocess_calculation_results(self, results_files):
        "Postprocess structure modeling job results"
        if self.number_of_templates == 1:
            # Every model is based on a separate template.
            for rf in results_files:
                m_file = rf['model_file']
                template_id = utils.standard_result_name(rf['template_ids'])
                num_updated_structure_models = StructureModel.objects\
                    .filter(modeling_job=self)\
                    .filter(templates__template_name=template_id)\
                    .update(status=StructureModel.FINISHED, file_path=m_file)
                if num_updated_structure_models != 1:
                    print(
                        'Problems when updating model based on %s.' % template_id
                        )
        else:
            # There is only 1 model, based on multiple templates.
            model_file = results_files[0]['model_file']
            templates = [
                utils.standard_result_name(r)
                for r in results_files[0]['template_ids'].split(',')
                ]
            structure_model = StructureModel.objects.get(modeling_job=self)
            if len(templates) != self.number_of_templates:
                logging.warning(
                    'Number of templates does not match in structure modeling '\
                        'job %s!',
                    self.name
                    )
                real_templates = Template.objects.filter(
                    search_job=self.search_job,
                    template_name__in=templates
                    )
                structure_model.templates.clear()
                structure_model.templates.add(*real_templates)
                # The problem that this sometimes can duplicate structure
                # models when impossible templates were selected is left here,
                # but if all COMER results will have structures (including Pfam
                # DB), this problem may dissapear.
            structure_model.status = StructureModel.FINISHED
            structure_model.file_path = model_file
            structure_model.save()
        # All structure models that are not in results files failed.
        Q = models.Q
        StructureModel.objects\
            .filter(modeling_job=self)\
            .filter(
                Q(status=StructureModel.NEW) | Q(status=StructureModel.RUNNING)
                )\
            .update(status=StructureModel.FAILED)

    def postprocess_failed_calculation(self):
        "Mark all models as failed if modeling job failed"
        structure_models = StructureModel.objects\
            .filter(modeling_job=self)\
            .update(status=StructureModel.FAILED)

    def get_model_matching_template_set(self, templates):
        "Retrieve structure model object matching given template set"
        existing_struct_models = StructureModel.objects\
            .select_related('modeling_job')\
            .annotate(num_templates=models.Count('templates'))\
            .filter(
                modeling_job__search_job=self.search_job,
                num_templates=len(templates)
                )\
            .prefetch_related('templates')
        new_model_template_set = sorted(templates, key=lambda t:t.id)
        for sm in existing_struct_models:
            sm_template_set = list(sm.templates.all().order_by('pk'))
            if sm_template_set == new_model_template_set:
                found_model = sm
                break
        else:
            found_model = None
        return found_model

    def templates(self):
        results_files = self.read_results_lst()
        return [r['template_ids'] for r in results_files]


class Template(models.Model):
    search_job = models.ForeignKey(SearchJob, on_delete=models.CASCADE)
    sequence_no = models.IntegerField()
    result_no = models.IntegerField()
    template_name = models.CharField(max_length=140)
    query_starts = models.IntegerField()
    query_ends = models.IntegerField()
    template_starts = models.IntegerField()
    template_ends = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['search_job', 'sequence_no', 'result_no'],
                name='unique_template'
                ),
            ]

    def __str__(self):
        s = 'Template %s (%s-%s), search job %s, query %s, result %s' % (
            self.template_name, self.template_starts, self.template_ends,
            self.search_job.name, self.sequence_no, self.result_no
            )
        return s


class StructureModel(models.Model):
    modeling_job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='structure_model'
        )
    templates = models.ManyToManyField(Template)
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
    file_path = models.CharField(max_length=1000, null=True)

    def __str__(self):
        r = 'Model based on %s' % self.printable_templates_list()
        return r

    def printable_templates_list(self):
        l = ','.join(
            [utils.standard_result_name(t.template_name)
                for t in self.templates.all()
                ]
            )
        return l

    def redo(self, new_modeling_job):
        "Try to do (failed) modeling again"
        self.status = self.NEW
        self.modeling_job = new_modeling_job
        self.save()


def save_structure_modeling_job(
        post_data, use_multiple_templates, example_name=None
        ):
    "Save data for structure modeling job"
    search_job = SearchJob.objects.get(name=post_data['job_id'])
    if example_name:
        job_name = example_name
    else:
        job_name = generate_job_name()
    sequence_no = int(post_data['sequence_no'])
    templates = sorted([int(t) for t in post_data.getlist('process')])
    modeller_key = post_data['modeller_key']
    # First, creating temporary modeling job that is not saved in the DB.
    modeling_job = Job(
        name=job_name, search_job=search_job,
        sequence_no=sequence_no,
        number_of_templates=len(templates) if use_multiple_templates else 1,
        )
    modeling_job
    model_all_pairs = not use_multiple_templates
    modeling_necessary, first_model = modeling_job.create_input_data(
        templates, model_all_pairs, modeller_key
        )
    if modeling_necessary:
        modeling_job.save()
    return search_job, first_model

