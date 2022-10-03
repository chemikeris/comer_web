import os

from django.test import TestCase

from apps.core import sequences
from apps.core import utils
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

