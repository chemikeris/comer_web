#! /usr/bin/env python3

import sys
import os
import unittest
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import get_comer_ws_backend_settings as s

class Test_parse_comer_ws_backend_config(unittest.TestCase):
    def setUp(self):
        test_config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'files', 'backend.conf'
            )
        with open(test_config_file, 'r') as f:
            self.test_config_str = f.read()

    def test_parse_comer_ws_backend_config(self):
        databases = s.parse_comer_ws_backend_config(self.test_config_str)
        self.assertIn('comer', databases)
        self.assertIn('hmmer', databases)
        self.assertIn('hhsuite', databases)

        self.assertEqual(
            databases['hmmer']['uniref50.fasta'], 'UniRef50_latest'
            )
        self.assertEqual(
            databases['hhsuite']['UniRef30_2020_03'], 'UniRef30_2020_03'
            )
        self.assertEqual(
            databases['comer']['pdb70_201216'], 'PDB70_201216'
            )
        self.assertEqual(databases['comer']['scop70_1.75'], 'SCOPe70_1.75')
        self.assertEqual(databases['comer']['pfamA_33.1'], 'Pfam_33.1')

    def test_nice_db_name(self):
        self.assertEqual('PDB70', s.nice_db_name('blabla_PDB_name'))
        self.assertEqual('UniRef', s.nice_db_name('blabla_uniref_name'))
        self.assertEqual('UniClust', s.nice_db_name('blabla_UniClust_name'))
        self.assertEqual('Pfam', s.nice_db_name('blabla_pfam_name'))
        self.assertEqual('SCOPe70', s.nice_db_name('blabla_scop_name'))
        self.assertEqual('MGnify_clusters', s.nice_db_name('blabla_mgy_name'))
        self.assertEqual('UniProtKB/SwissProt90', s.nice_db_name('blabla_SwissProt_name'))
        self.assertEqual('ECOD', s.nice_db_name('blabla_ECOD_F70_version'))
        logging.disable()
        self.assertIsNone(s.nice_db_name('blabla_ELSE_name'))
        logging.disable(logging.NOTSET)


if __name__ == '__main__':
    unittest.main()

