from django.core.management.base import BaseCommand, CommandError

from apps.databases import models as databases_models


class Command(BaseCommand):
    help = 'Load UniProt data from a local prepared file'
    # UniProt file line structure
    # uniprot_ac annotation in multiple words

    def add_arguments(self, parser):
        parser.add_argument('uniprot_file', help='UniProt annotations file')

    def handle(self, *args, **options):
        with open(options['uniprot_file']) as f:
            counter = 1
            for line in f:
                uniprot_ac, annotation = line.rstrip().split(' ', 1)
                print('Inserting UniProt entry %s: %s' % (counter, uniprot_ac))
                databases_models.UniProt.objects.update_or_create(
                    uniprot_ac=uniprot_ac,
                    annotation=annotation
                    )
                counter += 1

