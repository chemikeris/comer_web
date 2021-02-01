import copy
import os

from django.test import TestCase

from . import forms
from . import default
from . import models
from comer_web import settings

class TestInputValidation(TestCase):
    def setUp(self):
        self.form_data = copy.deepcopy(default.search_settings)
        self.form_data['sequence'] = 'SEQUENCE'
        self.form_data['number_of_results'] = 700
        # Setting default databases
        self.form_data['comer_db'] = settings.COMER_DATABASES[0][0]
        self.form_data['hhsuite_db'] = settings.HHSUITE_DATABASES[0][0]
        self.form_data['sequence_db'] = settings.SEQUENCE_DATABASES[0][0]

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

    def test_sequence_input_fasta_single(self):
        "Test single sequence fasta input"
        sequence = '>d1\ns'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], sequence)

    def test_sequence_input_fasta_msa(self):
        "Test multiple sequences alignment fasta input"
        sequence = '>d1\nss\n>d2\ns-'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], sequence)

    def test_sequence_input_fasta_with_unequal_sequences(self):
        "Test single sequence fasta input"
        sequence = '>d1\nsss\n>d2\ns'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], '>d1\nsss\n//\n>d2\ns')

    def test_multiple_sequences_input_with_incorrect_msa(self):
        "Test incorrect multiple sequences alignment fasta input"
        sequence = '>d1\nsds\n>d2\ns-\n//\n>d3\na'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertFalse(form.is_valid())

    def test_sequence_input_plain_text(self):
        "Test single sequence fasta input"
        sequence = 'SEQUENCE'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], sequence)

    def test_sequence_input_plain_text_with_gaps(self):
        "Test single sequence fasta input"
        sequence = 'S-E-Q-U-E-N-C-E'
        form_data = copy.deepcopy(self.form_data)
        form_data['sequence'] = sequence
        form = forms.SequencesInputForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sequence'], sequence)

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
        self.assertEqual(form.cleaned_data['sequence'], sequence)


class TestFunctions(TestCase):
    "Various tests for search app"
    def test_read_input_name_from_fasta(self):
        "Test reading input name from FASTA file"
        fname = os.path.join(settings.BASE_DIR, 'tests', 'files', 'fasta.fa')
        name, msa_input = models.read_input_name_and_type(fname)
        self.assertEqual(name, '3VHS_1')
        self.assertFalse(msa_input)

    def test_read_input_name_from_stockholm(self):
        "Test reading input name from Stockholm file"
        fname = os.path.join(
            settings.BASE_DIR, 'tests', 'files', 'stockholm.sto'
            )
        name, msa_input = models.read_input_name_and_type(fname)
        self.assertEqual(name, 'CBS domain')
        self.assertTrue(msa_input)

