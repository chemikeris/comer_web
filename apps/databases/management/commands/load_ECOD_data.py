import csv

from django.core.management.base import BaseCommand, CommandError

from apps.databases import models as databases_models


class Command(BaseCommand):
    help = 'Load ECOD data from a locally downloaded file'
    # ECOD file url: 
    # http://prodata.swmed.edu/ecod/distributions/ecod.latest.domains.txt

    def add_arguments(self, parser):
        parser.add_argument('ecod_file', help="ECOD data file")

    def handle(self, *args, **options):
        fieldnames = []
        delim = '\t'
        with open(options['ecod_file']) as f:
            for line in f:
                if line.startswith('#uid'):
                    fieldnames = line[1:].rstrip().split(delim)
                    break
            f.seek(0)
            reader = csv.DictReader(
                [line for line in f if line[0] != '#'],
                fieldnames=fieldnames, delimiter=delim
                )
            for ecod_entry in reader:
                e = ecod_entry
                print(
                    'Inserting ECOD entry %s, UID %s.' % (e['ecod_domain_id'],
                                                          e['uid']
                                                          )
                    )
                databases_models.ECOD.objects.update_or_create(
                    uid=ecod_entry['uid'],
                    ecod_domain_id=ecod_entry['ecod_domain_id']
                    )

