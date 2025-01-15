import os
import json
import logging

from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.databases.models import ECOD

def read_json_file(fname, filter_key=None):
    "Read JSON file contents into Python format"
    with open(fname) as f:
        try:
            contents = json.load(f)
        except json.JSONDecodeError as error:
            logging.error('JSON file unparsable: %s', fname)
            contents = None
            json_error = error
        else:
            json_error = None
    if filter_key is None or json_error:
        return contents, json_error
    else:
        return contents[filter_key], json_error


def search_input_files_exist(files):
    "Check if search input files exist"
    try:
        input_query_file = files['input_query_file']
    except KeyError:
        input_query_file = None
    try:
        input_parameters_file = files['input_search_parameters_file']
    except KeyError:
        input_parameters_file = None
    return input_query_file, input_parameters_file


def standard_result_name(name):
    "Convert results to standard IDs, mostly for UniProt"
    if name.startswith('sp|'):
        # This is SwissProt, getting UniProt AC from it.
        standard_name = name.split('|')[1]
    elif name.startswith('AF-'):
        # This is AlphaFold DB, getting UniProt AC from it.
        standard_name = name.split('-')[1]
    elif name.startswith('ECOD'):
        standard_name = name.split('_')[-1]
    else:
        # All other databases have only one representation.
        standard_name = name
    return standard_name


def is_Pfam_result(name):
    "Check if the result is a Pfam result"
    if name.startswith('PF'):
        return True
    else:
        return False


def is_CDD_result(name):
    "Check if the result is a Pfam result"
    if name.startswith('cd'):
        return True
    else:
        return False


def is_COG_KOG_result(name):
    "Check if the result is a Pfam result"
    if name.startswith('COG'):
        return True
    elif name.startswith('KOG'):
        return True
    else:
        return False


def suitable_for_structure_modeling(name):
    if is_Pfam_result(name):
        return False
    elif is_CDD_result(name):
        return False
    elif is_COG_KOG_result(name):
        return False
    else:
        return True


def get_object_or_404_for_removed_also(model, **kwargs):
    "Wrapper for get_object_or_404 that gives error 404 for removed jobs"
    m = get_object_or_404(model, **kwargs)
    if m.status == m.REMOVED:
        raise Http404
    else:
        return m


def format_gtalign_description(description):
    "Parse description from GTalign JSON"
    def parse_chain(chain_data):
        return chain_data.split(':')[1]
    def parse_model(model_data):
        return model_data[1:-1].split(':')[1]
    def trim_id(i):
        if i.endswith('.cif.gz'):
            return i.split('.')[0]
        elif i.endswith('.pdb.gz'):
            return i.split('.')[0]
        elif i.endswith('.ent'):
            return i.split('.')[0]
        elif i.endswith('.tar'):
            return i.split('.')[0]
        else:
            return i
    def afdb_id_to_uniprot(i):
        uniprot_ac = i.split('-')[1]
        return uniprot_ac
    def ecod_identifier_to_domain_name(i):
        ecod_uid = after_colon(i).split('.')[0]
        ecod_data = ECOD.objects.filter(uid=int(ecod_uid))[0]
        return ecod_data.ecod_domain_id
    def after_colon(i):
        return i.split(':')[1]
    parts = description.split()
    identifier = os.path.basename(parts[0])
    if identifier.startswith('ecod'):
        ecod_domain_name = ecod_identifier_to_domain_name(identifier)
        return ecod_domain_name
    elif identifier.startswith('scope'):
        identifier = trim_id(after_colon(identifier))
        return identifier
    elif identifier.startswith('swissprot') or identifier.startswith('uniref'):
        return afdb_id_to_uniprot(after_colon(identifier))
    elif identifier.startswith('UP'):
        id_parts = identifier.split(':')
        identifier = afdb_id_to_uniprot(id_parts[1])
        return '%s %a' % (identifier, trim_id(id_parts[0]))
    else:
        # Assuming PDB here
        if ':' in identifier:
            identifier = identifier.split(':')[1]
        identifier = trim_id(identifier)
        chain = parse_chain(parts[1])
        try:
            model = parse_model(parts[2])
        except IndexError:
            model = 1
        return '%s_%s_%s' % (identifier, chain, model)

