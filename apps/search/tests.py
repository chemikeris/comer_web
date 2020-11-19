import copy

from django.test import TestCase

from . import forms
from . import default

class TestInputValidation(TestCase):
    def test_default_sequence_form(self):
        form = forms.SequencesInputForm(default.search_settings)

    def test_default_msa_form(self):
        form = forms.MultipleAlignmentInputForm(default.search_settings)

    def test_hhsuite_settings(self):
        form_data = copy.deepcopy(default.search_settings)
        form_data['sequence'] = 'SEQUENCE'
        form_data['hhsuite_in_use'] = True
        # Testing empty number of iterations.
        form_with_empty_iterations = copy.deepcopy(form_data)
        form_with_empty_iterations['hhsuite_opt_niterations'] = None
        form = forms.BaseInputForm(form_with_empty_iterations)
        self.assertFalse(form.is_valid())
        # Testing empty E-value.
        form_with_empty_evalue = copy.deepcopy(form_data)
        form_with_empty_evalue['hhsuite_opt_evalue'] = None
        form = forms.BaseInputForm(form_with_empty_evalue)
        self.assertFalse(form.is_valid())
        
    def test_hmmer_settings(self):
        form_data = copy.deepcopy(default.search_settings)
        form_data['sequence'] = 'SEQUENCE'
        form_data['hmmer_in_use'] = True
        # Testing empty number of iterations.
        form_with_empty_iterations = copy.deepcopy(form_data)
        form_with_empty_iterations['hmmer_opt_niterations'] = None
        form = forms.BaseInputForm(form_with_empty_iterations)
        self.assertFalse(form.is_valid())
        # Testing empty E-value.
        form_with_empty_evalue = copy.deepcopy(form_data)
        form_with_empty_evalue['hmmer_opt_evalue'] = None
        form = forms.BaseInputForm(form_with_empty_evalue)
        self.assertFalse(form.is_valid())

