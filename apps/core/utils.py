import json
import logging

def read_json_file(fname):
    "Read JSON file contents into Python format"
    with open(fname) as f:
        try:
            contents = json.load(f)
        except json.JSONDecodeError as json_error:
            logging.error('JSON file unparsable: %s', fname)
            contents = None
    return contents

