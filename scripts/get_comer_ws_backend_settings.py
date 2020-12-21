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

import fabric


def nice_db_name(conf_name):
    "Convert DB name to nice representation"
    name = conf_name.split('_')[1]
    nice_names = {
        'pdb': 'Protein Data Bank',
        'uniref': 'UniRef',
        'uniclust': 'UniClust',
        'scop': 'SCOP',
        'pfam': 'PFAM',
        }
    nice_name = nice_names[name.lower()]
    return nice_name


def db_version(conf_value):
    version = conf_value.split('_', 1)[1]
    return version


def parse_comer_ws_backend_config(backend_config):
    "Parse comer-ws-backend settings file and retrieve available databases"
    c = configparser.ConfigParser()
    c.read_string('[values]\n' + backend_config)
    databases = {}
    databases['comer'] = []
    databases['hmmer'] = []
    databases['hhsuite'] = []
    for setting, value in c['values'].items():
        s, v = setting, value
        if s.startswith('seqdb'):
            logging.info('%s = %s', setting, value)
            databases['hmmer'].append(
                (v, '%s50 (%s)' % (nice_db_name(s), 'latest'))
                )
        elif s.startswith('hhsdb'):
            logging.info('%s = %s', setting, v)
            databases['hhsuite'].append(
                (v, '%s30 (%s)' % (nice_db_name(s), db_version(v)))
                )
        elif s.startswith('cprodb'):
            logging.info('%s = %s', setting, v)
            databases['comer'].append(
                (v, '%s (%s)' % (nice_db_name(s), db_version(v)))
                )
        else:
            continue
    return databases


def main(arguments):
    if (not arguments[1:]) or ('-h' in arguments) or ('--help' in arguments):
        print(__doc__)
        return

    if '--debug' in arguments[1:]:
        log_level = logging.DEBUG
        arguments.remove('--delete')
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)

    server_config_file = arguments[1]

    config = configparser.ConfigParser()
    config.read(server_config_file)

    if 'ssh_proxy_jump' in config:
        jump_connection = fabric.Connection(
            host=config['ssh_proxy_jump']['host'],
            port=config['ssh_proxy_jump']['port']
            )
    else:
        jump_connection = None
    connection = fabric.Connection(
        host=config['comer-ws-backend_server']['host'], gateway=jump_connection
        )
    backend_config_fd = io.BytesIO()
    connection.get(
        config['comer-ws-backend_path']['config'], local=backend_config_fd
        )
    backend_config = backend_config_fd.getvalue().decode()
    backend_config_fd.close()
    connection.close()

    databases = parse_comer_ws_backend_config(backend_config)

    print('COMER_DATABASES = %s' % databases['comer'])
    print('SEQUENCE_DATABASES = %s' % databases['hmmer'])
    print('HHSUITE_DATABASES = %s' % databases['hhsuite'])


if __name__ == '__main__':
    sys.exit(main(sys.argv))

