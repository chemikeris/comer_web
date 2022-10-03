import json
import logging

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

