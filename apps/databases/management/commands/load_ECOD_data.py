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
            counter = 1
            for ecod_entry in reader:
                e = ecod_entry
                print(
                    'Inserting ECOD entry %s: %s, UID %s.' % (
                        counter, e['ecod_domain_id'], e['uid']
                        )
                    )
                pdb_obj, created = databases_models.PDB\
                    .objects.get_or_create(id=e['pdb'])
                chain_obj, created = databases_models.Chain\
                    .objects.get_or_create(pdb=pdb_obj, chain=e['chain'])
                ecod_obj, created = databases_models.ECOD\
                    .objects.update_or_create(
                        uid=ecod_entry['uid'],
                        ecod_domain_id=ecod_entry['ecod_domain_id'],
                        )
                ecod_obj.pdb_chain = chain_obj
                # A
                annotation, created = databases_models.ECODAnnotation.objects\
                    .get_or_create(
                        ecod_hierarchy=databases_models.ECODAnnotation.A,
                        name=e['arch_name']
                        )
                ecod_obj.annotations.add(annotation)
                # X
                annotation, created = databases_models.ECODAnnotation.objects\
                    .get_or_create(
                        ecod_hierarchy=databases_models.ECODAnnotation.X,
                        name=e['x_name']
                        )
                ecod_obj.annotations.add(annotation)
                # H
                annotation, created = databases_models.ECODAnnotation.objects\
                    .get_or_create(
                        ecod_hierarchy=databases_models.ECODAnnotation.H,
                        name=e['h_name']
                        )
                ecod_obj.annotations.add(annotation)
                # T
                annotation, created = databases_models.ECODAnnotation.objects\
                    .get_or_create(
                        ecod_hierarchy=databases_models.ECODAnnotation.T,
                        name=e['t_name']
                        )
                ecod_obj.annotations.add(annotation)
                # F
                annotation, created = databases_models.ECODAnnotation.objects\
                    .get_or_create(
                        ecod_hierarchy=databases_models.ECODAnnotation.F,
                        name=e['f_name']
                        )
                ecod_obj.annotations.add(annotation)
                ecod_obj.save()
                counter += 1

