from django.core.management.base import BaseCommand, CommandError

from apps.databases import models as databases_models


class Command(BaseCommand):
    help = 'Load SCOPe data from a locally downloaded FASTA file'
    # SCOPe file URL
    # https://scop.berkeley.edu/downloads/scopeseq-2.08/astral-scopedom-seqres-gd-sel-gs-bib-40-2.08.fa

    def add_arguments(self, parser):
        parser.add_argument('scop_file', help='SCOPe FASTA file')

    def handle(self, *args, **options):
        with open(options['scop_file']) as f:
            for line in f:
                if line.startswith('>'):
                    domain_id, annotation = line.rstrip()[1:].split(' ', 1)
                    print(
                        'Inserting annotation for %s (%s)' % (domain_id,
                                                              annotation)
                        )
                    databases_models.SCOP.objects.update_or_create(
                        domain_id=domain_id, annotation=annotation
                        )

