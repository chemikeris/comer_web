from django.test import TestCase

# Create your tests here.

from .models import format_description

class Test_GTalign_JSON_description_formatting(TestCase):
    "Test parsing and formatting descriptions from GTalign JSON"
    def test_parsing_PDB_description(self):
        desc = "/databases/wwpdb/mmCIF/hw/1hwg.cif.gz Chn:A (M:1)"
        expected_description = '1hwg_A_1'
        formatted_description = format_description(desc)
        self.assertEqual(formatted_description, expected_description)

    def test_parsing_SCOPe_description(self):
        desc = '/databases/scope/scope40_208/scope40_208.tar:d2xzga2.ent Chn:A'
        expected_description = 'd2xzga2'
        formatted_description = format_description(desc)
        self.assertEqual(formatted_description, expected_description)

    def test_parsing_SwissProt_description(self):
        desc = "/databases/swissprot/swissprot_v4/swissprot_pdb_v4.tar:AF-P50187-F1-model_v4.pdb.gz Chn:A (M:1)"
        expected_description = 'P50187'
        formatted_description = format_description(desc)
        self.assertEqual(formatted_description, expected_description)

    def test_parsing_UniRef_description(self):
        desc = "/data/AFDBv4/uniref30/uniref30__1408.tar:AF-A0A1H7WXF0-F1-model_v4.cif.gz Chn:A (M:1)"
        expected_description = 'A0A1H7WXF0'
        formatted_description = format_description(desc)
        self.assertEqual(formatted_description, expected_description)

