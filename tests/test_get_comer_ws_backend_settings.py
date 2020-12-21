#! /usr/bin/env python3

import sys
import os
import unittest

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

        self.assertIn(
            ('uniref50.fasta', 'UniRef50 (latest)'), databases['hmmer']
            )
        self.assertIn(
            ('UniRef30_2020_03', 'UniRef30 (2020_03)'), databases['hhsuite']
            )
        self.assertIn(
            ('pdb70_201216', 'Protein Data Bank (201216)'), databases['comer']
            )
        self.assertIn(('scop70_1.75', 'SCOP (1.75)'), databases['comer'])
        self.assertIn(('pfamA_33.1', 'PFAM (33.1)'), databases['comer'])

    def test_nice_db_name(self):
        self.assertEqual('Protein Data Bank', s.nice_db_name('blabla_PDB_name'))
        self.assertEqual('UniRef', s.nice_db_name('blabla_uniref_name'))
        self.assertEqual('UniClust', s.nice_db_name('blabla_UniClust_name'))
        self.assertEqual('PFAM', s.nice_db_name('blabla_pfam_name'))
        self.assertEqual('SCOP', s.nice_db_name('blabla_scop_name'))



if __name__ == '__main__':
    unittest.main()

