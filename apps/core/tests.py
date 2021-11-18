import os

from django.test import TestCase

from apps.core import sequences
from comer_web import settings


class TestSequencesTools(TestCase):
    "Test tools that manipulate sequences data"
    def test_summarize_fasta_msa1(self):
        "Test summarizing MSA in FASTA format"
        fname = os.path.join(settings.BASE_DIR, 'tests', 'files', 'fasta.fa')
        number_of_sequences = sequences.summarize_msa(fname)
        self.assertEqual(number_of_sequences, 1)

    def test_summarize_fasta_msa2(self):
        "Test summarizing MSA in FASTA format"
        fname = os.path.join(
            settings.BASE_DIR, 'tests', 'files',
            'comer_result_alignment_1.fasta'
            )
        number_of_sequences = sequences.summarize_msa(fname)
        self.assertEqual(number_of_sequences, 2)

    def test_summarize_stockholm_msa(self):
        "Test summarizing MSA in Stockholm format"
        fname = os.path.join(
            settings.BASE_DIR, 'tests', 'files', 'stockholm.sto'
            )
        number_of_sequences = sequences.summarize_msa(fname)
        self.assertEqual(number_of_sequences, 5)

    def test_read_neff_file(self):
        fname = os.path.join(settings.BASE_DIR, 'tests', 'files', 'neff')
        n, neff, identity = sequences.read_neff_file(fname)
        self.assertEqual(n, 6)
        self.assertEqual(neff, 2.00)
        self.assertEqual(identity, 0.62)

