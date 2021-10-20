import copy
import os
import tempfile
import json
import shutil

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from . import forms
from . import default
from . import models
from comer_web import settings
from comer_web.calculation_server import read_config_file

class TestInputValidation(TestCase):
    def setUp(self):
        self.form_data = copy.deepcopy(default.search_settings)
        self.form_data['sequence'] = 'SEQUENCE'
        self.form_data['number_of_results'] = 700
        # Setting default databases
        self.form_data['comer_db'] = [settings.COMER_DATABASES[0][0]]
        self.form_data['hhsuite_db'] = settings.HHSUITE_DATABASES[0][0]
        self.form_data['sequence_db'] = settings.SEQUENCE_DATABASES[0][0]
        self.form_data['cother_db'] = [settings.COTHER_DATABASES[0][0]]

    def test_default_sequences_form(self):
        form = forms.SequencesInputForm(default.search_settings)

    def test_hhsuite_settings(self):
        self.form_data['hhsuite_in_use'] = True
        # Testing empty number of iterations.
        form_with_empty_iterations = copy.deepcopy(self.form_data)
        form_with_empty_iterations['hhsuite_opt_niterations'] = None
        form = forms.SequencesInputForm(form_with_empty_iterations)
        self.assertFalse(form.is_valid())
        # Testing empty E-value.
        form_with_empty_evalue = copy.deepcopy(self.form_data)
        form_with_empty_evalue['hhsuite_opt_evalue'] = None
        form = forms.SequencesInputForm(form_with_empty_evalue)
        self.assertFalse(form.is_valid())
        # Testing good form.
        self.form_data['hhsuite_opt_niterations'] = 2
        self.form_data['hhsuite_opt_evalue'] = 1e-3
        form = forms.SequencesInputForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_hmmer_settings(self):
        self.form_data['hmmer_in_use'] = True
        # Testing empty number of iterations.
        form_with_empty_iterations = copy.deepcopy(self.form_data)
        form_with_empty_iterations['hmmer_opt_niterations'] = None
        form = forms.SequencesInputForm(form_with_empty_iterations)
        self.assertFalse(form.is_valid())
        # Testing empty E-value.
        form_with_empty_evalue = copy.deepcopy(self.form_data)
        form_with_empty_evalue['hmmer_opt_evalue'] = None
        form = forms.SequencesInputForm(form_with_empty_evalue)
        self.assertFalse(form.is_valid())
        # Testing good form.
        self.form_data['hmmer_opt_niterations'] = 2
        self.form_data['hmmer_opt_evalue'] = 1e-3
        form = forms.SequencesInputForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_fail_with_empty_sequence_input_and_no_file(self):
        "Test no input failure"
        sequence = ''
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        valid_form = form.is_valid()
        self.assertFalse(valid_form)

    def test_sequence_input_fasta_single(self):
        "Test single sequence fasta input"
        sequence = '>d1\ns'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], [sequence])

    def test_sequence_input_fasta_msa(self):
        "Test multiple sequences alignment fasta input"
        sequence = '>d1\nss\n>d2\ns-'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], [sequence])

    def test_sequence_input_fasta_with_unequal_sequences(self):
        "Test single sequence fasta input"
        sequence = '>d1\nsss\n>d2\ns'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form_data['multi_sequence_fasta'] = True
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], ['>d1\nsss', '>d2\ns'])

    def test_sequence_input_plain_text(self):
        "Test single sequence fasta input"
        sequence = 'SEQUENCE'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], [sequence])

    def test_sequence_input_plain_text_with_gaps(self):
        "Test single sequence fasta input"
        sequence = 'S-E-Q-U-E-N-C-E'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], [sequence])

    def test_sequence_input_plain_text_wrong(self):
        "Test single sequence fasta input"
        sequence = 'SEQUENCE1'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertFalse(form.is_valid())

    def test_sequence_input_fasta_and_plain(self):
        "Test single sequence fasta input"
        sequence = '>d1\nfasta\n//\nplain'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['sequence'], ['>d1\nfasta', 'plain']
            )

    def test_comer_profile_input_for_cother_search(self):
        "Test if COMER profile input is allowed for COTHER search"
        profile = 'COMER profile v2.0\nDESC: test\n'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = profile
        form_data['use_cother'] = True
        form = forms.SequencesInputForm(form_data)
        self.assertFalse(form.is_valid())

    def test_cother_profile_input_for_comer_search(self):
        "Test if COTHER profile input is allowed for COMER search"
        profile = 'COTHER profile v2.5\nDESC: test\n'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = profile
        form_data['use_cother'] = False
        form = forms.SequencesInputForm(form_data)
        self.assertFalse(form.is_valid())

    def test_input_file(self):
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = None
        form_files = {}
        f = tempfile.NamedTemporaryFile()
        s = '>s\nA'
        form_files['input_query_file'] = SimpleUploadedFile(f.name, s.encode())
        form = forms.SequencesInputForm(form_data, form_files)
        valid_form = form.is_valid()
        self.assertTrue(valid_form)
        self.assertEqual(form.cleaned_data['sequence'], [s])

    def test_input_both_text_and_file(self):
        form_files = {}
        f = tempfile.NamedTemporaryFile()
        s = '>s\nA'
        form_files['input_query_file'] = SimpleUploadedFile(f.name, s.encode())
        form = forms.SequencesInputForm(self.form_data, form_files)
        valid_form = form.is_valid()
        self.assertTrue(valid_form)
        self.assertEqual(
            form.cleaned_data['sequence'],
            [self.form_data['sequence'], s]
            )


class TestApi(TestCase):
    "Test search API functionality"
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        if hasattr(self, 'job'):
            directory_to_remove = self.job.get_directory()
            shutil.rmtree(directory_to_remove)

    def test_empty_input(self):
        "Test empty query, it should fail"
        response = self.client.post('/search/api/submit', {})
        response_json = json.loads(response.content)
        self.assertFalse(response_json['success'])

    def test_sequence_input_only(self):
        "Query with sequence only should be successful"
        sequence = 'SEQUENCE'
        response = self.client.post(
            '/search/api/submit', {'sequence': sequence}
            )
        response_json = json.loads(response.content)
        self.job = models.Job.objects.get(name=response_json['job_id'])
        self.assertTrue(response_json['success'])

    def test_input_sequence_and_change_SHOW(self):
        "Query with sequence only should be successful"
        sequence = 'SEQUENCE'
        response = self.client.post(
            '/search/api/submit', {'sequence': sequence, 'SHOW': False}
            )
        response_json = json.loads(response.content)
        self.job = models.Job.objects.get(name=response_json['job_id'])
        self.assertTrue(response_json['success'])
        job_options = read_config_file(self.job.get_input_file('options'))
        self.assertFalse(job_options.getboolean('OPTIONS', 'SHOW'))


class TestFunctions(TestCase):
    "Various tests for search app"
    def test_read_input_name_from_fasta(self):
        "Test reading input name from FASTA file"
        fname = os.path.join(settings.BASE_DIR, 'tests', 'files', 'fasta.fa')
        name, input_format, desc = models.read_input_name_and_type(fname)
        self.assertEqual(name, '3VHS_1')
        self.assertEqual(input_format, 'Fasta')
        self.assertEqual(desc, 'sequence')

    def test_read_input_name_from_stockholm(self):
        "Test reading input name from Stockholm file"
        fname = os.path.join(
            settings.BASE_DIR, 'tests', 'files', 'stockholm.sto'
            )
        name, input_format, desc = models.read_input_name_and_type(fname)
        self.assertEqual(name, 'CBS domain')
        self.assertEqual(input_format, 'Stockholm')
        self.assertEqual(desc, 'multiple sequence alignment')

