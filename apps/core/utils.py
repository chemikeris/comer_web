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
    if filter_key is None:
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

