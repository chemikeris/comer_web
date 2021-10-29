"""Demo script for COMER web server API.
"""

import sys
import os
import urllib.request, urllib.error, urllib.parse
import json
import argparse
import time
import logging
logging.basicConfig(level=logging.INFO)


def connect_to_server(url, data=None, raw=False):
    "Connect to COMER server"
    if data is None:
        logging.debug(url)
    else:
        logging.debug('%s?%s', url, data)
    try:
        connection = urllib.request.urlopen(url, data)
    except urllib.error.URLError as err:
        logging.error('Could not connect to %s: %s', url, str(err))
        data = ''
    else:
        if raw:
            data = connection.read().decode()
        else:
            data = json.loads(connection.read())
        connection.close()
    return data


def format_comer_url(what_for, comer_ws_url):
    "Format COMER web server API url"
    if what_for == 'submit':
        url = f'{comer_ws_url}/search/api/submit'
    elif what_for == 'job_status':
        url = f'{comer_ws_url}/search/api/job_status'
    elif what_for == 'results':
        url = f'{comer_ws_url}/search/api/results_json'
    else:
        url = comer_ws_url
    return url


def main():
    demo_sequence = 'TKPCQSDKDCKKFACRKPKVPKCINGFCKCVR'

    arguments_parser = argparse.ArgumentParser(description=__doc__)
    arguments_parser.add_argument('-s', '--sequence', default=demo_sequence)
    arguments_parser.add_argument(
        '--url', default='https://bioinformatics.lt/comer',
        help='COMER web server URL'
        )
    args = arguments_parser.parse_args()

    submit_url = format_comer_url('submit', args.url)
    job_status_url = format_comer_url('job_status', args.url)
    results_url = format_comer_url('results', args.url)

    logging.info('Submitting data to %s', submit_url)
    submit_data = connect_to_server(
        submit_url,
        f'sequence={args.sequence}'.encode()
        )
    if submit_data['success']:
        job_id = submit_data['job_id']
        logging.info('Submitted job %s' % job_id)
        job_finished_or_failed = False
        current_job_status_url = f'{job_status_url}/{job_id}'
        logging.info('Querying job status at %s' % current_job_status_url)
        logging.info('Waiting for results.')
        while not job_finished_or_failed:
            job_status_data = connect_to_server(current_job_status_url)
            if job_status_data['success']:
                if job_status_data['status'] == 'finished':
                    job_finished_or_failed = True
                    logging.info('Job finished successfully.')
                    current_results_url = f'{results_url}/{job_id}'
                    results = connect_to_server(current_results_url, raw=True)
                    print(results)
                elif job_status_data['status'] == 'failed':
                    job_finished_or_failed = True
                    logging.error('Job failed!')
                    logging.error(job_status_data['log'])
                else:
                    time.sleep(10)
            else:
                logging.error('Unexpected situation while getting job status!')
                break
    else:
        logging.error('Connecting to COMER server failed!')
        for field, errors in submit_data['form_errors'].items():
            for e in errors:
                logging.error('Field %s, error: %s', field, e)


if __name__ == '__main__':
    sys.exit(main())

