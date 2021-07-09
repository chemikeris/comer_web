import json
import logging

def read_json_file(fname, filter_key=None):
    "Read JSON file contents into Python format"
    with open(fname) as f:
        try:
            contents = json.load(f)
        except json.JSONDecodeError as json_error:
            logging.error('JSON file unparsable: %s', fname)
            contents = None
    if filter_key is None:
        return contents
    else:
        return contents[filter_key]

