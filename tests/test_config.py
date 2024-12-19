import unittest

from comer_web.calculation_server import read_config_file, SERVER_CONFIG_FILE


class Test_config_file(unittest.TestCase):
    "Test config file"
    def test_config_file_contents(self):
        "Test if config file contains necessary settings"
        config = read_config_file(SERVER_CONFIG_FILE)
        self.assertTrue('comer-ws-backend_server' in config)
        # comer-ws-backend config
        comer_ws_backend_config = config['comer-ws-backend_path']
        self.assertTrue('search_executable' in comer_ws_backend_config)
        self.assertTrue('cother_search_executable' in comer_ws_backend_config)
        self.assertTrue('model_structure_executable' in comer_ws_backend_config)
        self.assertTrue('msa_executable' in comer_ws_backend_config)
        self.assertTrue('config' in comer_ws_backend_config)
        self.assertTrue('jobs_directory' in comer_ws_backend_config)
        # gtalign-ws-backend config
        gtalign_ws_backend_config = config['gtalign-ws-backend_path']
        self.assertTrue('structure_search_executable' in gtalign_ws_backend_config)
        self.assertTrue('msa_executable' in gtalign_ws_backend_config)
        self.assertTrue('config' in gtalign_ws_backend_config)
        # local paths
        local_paths = config['local_paths']
        self.assertTrue('structures_directory' in local_paths)

