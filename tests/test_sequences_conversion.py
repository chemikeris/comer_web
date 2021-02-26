import os
import unittest

from comer_web import utils
from comer_web import sequences

class Test_convert_comer_json_to_fasta(unittest.TestCase):
    def setUp(self):
        self.data_directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'files'
            )
        self.results_file = os.path.join(
            self.data_directory, 'comer_search_results.json'
            )

    def test_sequence_alignment_1_to_fasta(self):
        results_json = utils.read_json_file(self.results_file)
        fasta_from_json = sequences.comer_json_hit_record_to_alignment(
            results_json['comer_search']['query']['description'],
            results_json['comer_search']['search_hits'][0]['hit_record']
            )
        expected_fasta_file = os.path.join(
            self.data_directory, 'comer_result_alignment_1.fasta'
            )
        expected_fasta_str = read_expected_fasta(expected_fasta_file)
        self.assertEqual(fasta_from_json, expected_fasta_str)

    def test_sequence_alignment_2_to_fasta(self):
        results_json = utils.read_json_file(self.results_file)
        fasta_from_json = sequences.comer_json_hit_record_to_alignment(
            results_json['comer_search']['query']['description'],
            results_json['comer_search']['search_hits'][1]['hit_record']
            )
        expected_fasta_file = os.path.join(
            self.data_directory, 'comer_result_alignment_2.fasta'
            )
        expected_fasta_str = read_expected_fasta(expected_fasta_file)
        self.assertEqual(fasta_from_json, expected_fasta_str)


def read_expected_fasta(fasta_file):
    with open(fasta_file) as f:
        expected_fasta = f.read().strip()
    return expected_fasta

