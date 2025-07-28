import os

from django.test import TestCase

from apps.core import sequences
from apps.core import utils
from comer_web import settings

import apps.core.management.commands.get_comer_ws_backend_databases as get_dbs


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


class TestUtils(TestCase):
    "Test utilities"
    def test_SwissProt_name_conversion(self):
        sp_name = 'sp|Q9Y6K1|DNM3A_HUMAN'
        uniprot_ac = 'Q9Y6K1'
        self.assertEqual(utils.standard_result_name(sp_name), uniprot_ac)

    def test_AlphaFoldDB_name_conversion(self):
        alphafold_db_name = 'AF-Q9Y6K1-F1'
        uniprot_ac = 'Q9Y6K1'
        self.assertEqual(
            utils.standard_result_name(alphafold_db_name), uniprot_ac
            )

    def test_ECOD_name_conversion(self):
        db_name = 'ECOD_000000294_e1qvcA1'
        ecod_domain_name = 'e1qvcA1'
        self.assertEqual(
            utils.standard_result_name(db_name), ecod_domain_name
            )

    def test_if_it_is_Pfam_result(self):
        pfam_id = 'PF11325.10'
        pdb_id = '2F9Q'
        ccd_id = 'cd04496'
        cog_id = 'COG2965'
        kog_id = 'KOG1653'
        self.assertTrue(utils.is_Pfam_result(pfam_id))
        self.assertFalse(utils.is_Pfam_result(pdb_id))
        self.assertFalse(utils.is_Pfam_result(ccd_id))
        self.assertFalse(utils.is_Pfam_result(cog_id))
        self.assertFalse(utils.is_Pfam_result(kog_id))

    def test_if_it_is_CDD_result(self):
        pfam_id = 'PF11325.10'
        pdb_id = '2F9Q'
        cdd_id = 'cd04496'
        cog_id = 'COG2965'
        kog_id = 'KOG1653'
        self.assertTrue(utils.is_CDD_result(cdd_id))
        self.assertFalse(utils.is_CDD_result(pfam_id))
        self.assertFalse(utils.is_CDD_result(pdb_id))
        self.assertFalse(utils.is_CDD_result(cog_id))
        self.assertFalse(utils.is_CDD_result(kog_id))

    def test_if_it_is_COG_result(self):
        pfam_id = 'PF11325.10'
        pdb_id = '2F9Q'
        cdd_id = 'cd04496'
        cog_id = 'COG2965'
        kog_id = 'KOG1653'
        self.assertTrue(utils.is_COG_KOG_result(cog_id))
        self.assertTrue(utils.is_COG_KOG_result(kog_id))
        self.assertFalse(utils.is_COG_KOG_result(cdd_id))
        self.assertFalse(utils.is_COG_KOG_result(pfam_id))
        self.assertFalse(utils.is_COG_KOG_result(pdb_id))

    def test_if_result_is_suitable_for_structure_modeling(self):
        uniprot_ac = 'Q9Y6K1'
        pdb_id = '2F9Q'
        scope_id = 'd3tqya_'
        ecod_name = 'ECOD_000000294_e1qvcA1'
        pfam_id = 'PF11325.10'
        cdd_id = 'cd04496'
        cog_id = 'COG2965'
        kog_id = 'KOG1653'
        self.assertTrue(utils.suitable_for_structure_modeling(uniprot_ac))
        self.assertTrue(utils.suitable_for_structure_modeling(pdb_id))
        self.assertTrue(utils.suitable_for_structure_modeling(scope_id))
        self.assertTrue(utils.suitable_for_structure_modeling(ecod_name))
        self.assertFalse(utils.suitable_for_structure_modeling(pfam_id))
        self.assertFalse(utils.suitable_for_structure_modeling(cdd_id))
        self.assertFalse(utils.suitable_for_structure_modeling(cog_id))
        self.assertFalse(utils.suitable_for_structure_modeling(kog_id))

    def test_split_gtalign_description(self):
        description = '/path/to/file.pdb Chn:A (M:1)'
        expected_output = ('/path/to/file.pdb', 'A', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_no_model(self):
        description = '/path/to/file.pdb Chn:A'
        expected_output = ('/path/to/file.pdb', 'A', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_no_model_no_chain(self):
        description = '/path/to/file.pdb'
        expected_output = ('/path/to/file.pdb', None, 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_with_spaces(self):
        description = '/path/to/file name.pdb Chn:A (M:1)'
        expected_output = ('/path/to/file name.pdb', 'A', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_no_model_with_spaces(self):
        description = '/path/to/file name.pdb Chn:A'
        expected_output = ('/path/to/file name.pdb', 'A', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_no_model_no_chain_with_spaces(self):
        description = '/path/to/file name.pdb'
        expected_output = ('/path/to/file name.pdb', None, 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_chain_space(self):
        description = '/path/to/file.pdb Chn: (M:1)'
        expected_output = ('/path/to/file.pdb', ' ', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_chain_space_no_model(self):
        description = '/path/to/file.pdb Chn: '
        expected_output = ('/path/to/file.pdb', ' ', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)

    def test_split_gtalign_description_with_spaces_and_chain_space(self):
        description = '/path/to/file name.pdb Chn:  (M:1)'
        expected_output = ('/path/to/file name.pdb', ' ', 1)
        parts = utils.split_gtalign_description(description)
        self.assertEqual(expected_output, parts)


class TestParsingCalculationServerConfig(TestCase):
    "Test parsing calculation server config file"
    def test_reading_db_data_pdb_comer(self):
        name, version = get_dbs.db_name_and_version(
            'cprodb_pdb_name', 'pdb70_240312'
            )
        self.assertEqual(name, 'pdb')
        self.assertEqual(version, '240312')

    def test_reading_db_data_pdb_gtalign(self):
        name, version = get_dbs.db_name_and_version(
            'strdb_pdb_name', 'mmCIF', for_gtalign=True
            )
        self.assertEqual(name, 'pdb_mmcif')
        self.assertIsNone(version)

    def test_reading_db_data_pdb_plus_gtalign(self):
        name, version = get_dbs.db_name_and_version(
            'strdb_pdb_scop_ecod_name', 'mmCIF|scope40_208|ecod_20240325_F70',
            for_gtalign=True
            )
        self.assertEqual(name, 'pdb_scop_ecod')
        self.assertIsNone(version)


class Test_GTalign_JSON_description_formatting(TestCase):
    "Test parsing and formatting descriptions from GTalign JSON"
    def test_parsing_PDB_description(self):
        desc = "/databases/wwpdb/mmCIF/hw/1hwg.cif.gz Chn:A (M:1)"
        expected_description = '1hwg_A_1'
        formatted_description = utils.format_gtalign_description(desc)
        self.assertEqual(formatted_description, expected_description)

    def test_parsing_SCOPe_description(self):
        desc = '/databases/scope/scope40_208/scope40_208.tar:d2xzga2.ent Chn:A'
        expected_description = 'd2xzga2'
        formatted_description = utils.format_gtalign_description(desc)
        self.assertEqual(formatted_description, expected_description)

    def test_parsing_SwissProt_description(self):
        desc = "/databases/swissprot/swissprot_v4/swissprot_pdb_v4.tar:AF-P50187-F1-model_v4.pdb.gz Chn:A (M:1)"
        expected_description = 'P50187'
        formatted_description = utils.format_gtalign_description(desc)
        self.assertEqual(formatted_description, expected_description)

    def test_parsing_UniRef_description(self):
        desc = "/data/AFDBv4/uniref30/uniref30__1408.tar:AF-A0A1H7WXF0-F1-model_v4.cif.gz Chn:A (M:1)"
        expected_description = 'A0A1H7WXF0'
        formatted_description = utils.format_gtalign_description(desc)
        self.assertEqual(formatted_description, expected_description)

