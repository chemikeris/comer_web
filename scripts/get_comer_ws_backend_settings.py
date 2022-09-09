#! /usr/bin/env python3
"""Get Comer web server backend settings from the calculation server.

Usage:
$0 server_config.ini
"""

import sys
import os
import configparser
import io
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comer_web import calculation_server


def nice_db_name(conf_name, suffix=None):
    "Convert DB name to nice representation"
    name = conf_name.split('_')[1]
    nice_names = {
        'pdb': 'PDB70',
        'uniref': 'UniRef',
        'uniclust': 'UniClust',
        'scop': 'SCOPe70',
        'pfam': 'Pfam',
        'mgy': 'MGnify_clusters',
        'swissprot': 'UniProtKB/SwissProt90',
        'ecod': 'ECOD-F70',
        'cog': 'COG-KOG',
        'ncbicd': 'NCBI-Conserved-Domains',
        }
    try:
        nice_name = nice_names[name.lower()]
    except KeyError:
        logging.warning('Unknown database name: %s', name)
        return None
    if suffix:
        if name.lower() == 'mgy':
            pass
        else:
            nice_name += suffix
    return nice_name


def db_version(conf_value):
    try:
        version = conf_value.split('_', 1)[1]
    except IndexError:
        version = None
    return version


def parse_comer_ws_backend_config(backend_config):
    "Parse comer-ws-backend settings file and retrieve available databases"
    c = configparser.ConfigParser()
    c.read_string('[values]\n' + backend_config)
    databases = configparser.ConfigParser()
    databases.optionxform = str
    databases['comer'] = {}
    databases['cother'] = {}
    databases['hmmer'] = {}
    databases['hhsuite'] = {}
    for setting, value in c['values'].items():
        s, v = setting, value
        if s.startswith('seqdb'):
            logging.info('%s = %s', setting, value)
            databases['hmmer'][v] = nice_db_name(s, '50_latest')
        elif s.startswith('hhsdb'):
            logging.info('%s = %s', setting, v)
            databases['hhsuite'][v] = nice_db_name(s, '30_'+db_version(v))
        elif s.startswith('cprodb'):
            logging.info('%s = %s', setting, v)
            nice_name = nice_db_name(s)
            version = db_version(v)
            if version:
                databases['comer'][v] = '%s_%s' % (nice_name, version)
            else:
                databases['comer'][v] = nice_name
        elif s.startswith('cotherprodb'):
            logging.info('%s = %s', setting, v)
            databases['cother'][v] = '%s_%s' % (nice_db_name(s), db_version(v))
        else:
            continue
    return databases


def main(arguments):
    if ('-h' in arguments) or ('--help' in arguments):
        print(__doc__)
        return

    if '--debug' in arguments[1:]:
        log_level = logging.DEBUG
        arguments.remove('--debug')
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)

    try:
        server_config_file = arguments[1]
    except IndexError:
        server_config_file = calculation_server.SERVER_CONFIG_FILE

    server_connection = calculation_server.Connection(server_config_file)
    backend_config_fd = io.BytesIO()
    server_connection.connection.get(
        server_connection.config['comer-ws-backend_path']['config'],
        local=backend_config_fd
        )
    backend_config = backend_config_fd.getvalue().decode()
    backend_config_fd.close()

    databases = parse_comer_ws_backend_config(backend_config)
    databases.write(sys.stdout)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

