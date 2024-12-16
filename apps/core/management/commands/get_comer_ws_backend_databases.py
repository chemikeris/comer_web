import sys
import os
import configparser
import io
import logging

from django.core.management.base import BaseCommand, CommandError

from comer_web import calculation_server
from apps.core.models import Databases


class Command(BaseCommand):
    help = 'Retrieve current databases from calculation server'

    def add_arguments(self, parser):
        parser.add_argument('--silent', action='store_true')

    def handle(self, *args, **options):
        "Connect to calculation server, get and parse DB info"
        if not options['silent']:
            logging.basicConfig(level=logging.INFO)
        backend_software = ['comer', 'gtalign']
        for software in backend_software:
            backend_config = retrieve_calculation_server_config(software)
            databases_info = parse_comer_ws_backend_config(backend_config)
            write_or_update(databases_info)


def retrieve_calculation_server_config(software='comer'):
    "Retrieve calculation server config"
    server_config_file = calculation_server.SERVER_CONFIG_FILE
    server_connection = calculation_server.Connection(server_config_file)
    backend_config_fd = io.BytesIO()
    software_paths_str = '%s-ws-backend_path' % software
    server_connection.connection.get(
        server_connection.config[software_paths_str]['config'],
        local=backend_config_fd
        )
    backend_config = backend_config_fd.getvalue().decode()
    backend_config_fd.close()
    return backend_config


def db_name_and_version(conf_name, conf_value, uniref_suffix=None,
                        for_gtalign=False):
    parts = conf_name.split('_')
    name = parts[1]
    if name == 'bfd':
        version = None
    elif name == 'pdb':
        if for_gtalign:
            if len(parts) > 3:
                name = '_'.join(parts[1:-1])
                version = None
            else:
                name = 'pdb_mmcif'
                version = None
        else:
            version = db_version(conf_value)
    else:
        version = db_version(conf_value)
    if name == 'uniref' and uniref_suffix:
        name = name + uniref_suffix
    return name, version


def db_version(conf_value):
    "Parse DB version from calculation server config value"
    try:
        version = conf_value.split('_', 1)[1]
    except IndexError:
        version = None
    return version


def parse_comer_ws_backend_config(backend_config):
    "Parse comer-ws-backend settings file and retrieve available databases"
    c = configparser.ConfigParser()
    c.read_string('[values]\n' + backend_config)
    databases = {}
    databases['comer'] = {}
    databases['cother'] = {}
    databases['hmmer'] = {}
    databases['hhsuite'] = {}
    databases['gtalign'] = {}
    version_not_necessary = []
    for setting, value in c['values'].items():
        s, v = setting, value
        if s.startswith('seqdb'):
            logging.info('%s = %s', setting, value)
            name, version = db_name_and_version(s, v, '50')
            if name == 'mgy':
                version = version.lstrip('clusters_')
            version = version.rsplit('.', 1)[0]
            databases['hmmer'][v] = name, version
        elif s.startswith('hhsdb'):
            logging.info('%s = %s', setting, v)
            databases['hhsuite'][v] = db_name_and_version(s, v, '30')
        elif s.startswith('cprodb'):
            logging.info('%s = %s', setting, v)
            databases['comer'][v] = db_name_and_version(s, v)
        elif s.startswith('cotherprodb'):
            logging.info('%s = %s', setting, v)
            databases['cother'][v] = db_name_and_version(s, v)
        elif s.startswith('strdb'):
            logging.info('%s = %s', setting, v)
            databases['gtalign'][v] = db_name_and_version(
                s, v, for_gtalign=True
                )
        else:
            continue
    return databases


def write_or_update(databases_info):
    "Write databases info to web server DB"
    for program, db_info in databases_info.items():
        if db_info:
            logging.info('Saving search databases for %s.', program)
        for backend_name, info in db_info.items():
            db, version = info
            logging.info(
                'DB %s, version %s, description %s', db, version, backend_name
                )
            Databases.objects.update_or_create(
                program=program,
                db=db,
                defaults={
                    'calculation_server_description': backend_name,
                    'version': version
                    }
                )

