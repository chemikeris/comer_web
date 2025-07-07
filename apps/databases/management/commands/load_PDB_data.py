from django.core.management.base import BaseCommand, CommandError

from apps.databases import models as databases_models


class Command(BaseCommand):
    help = 'Load PDB data from a locally downloaded PDB SEQRES file'
    # PDB SEQRES file url: 
    # https://files.wwpdb.org/pub/pdb/derived_data/pdb_seqres.txt

    def add_arguments(self, parser):
        parser.add_argument('pdb_seqres_file', help="PDB SEQRES file")

    def handle(self, *args, **options):
        with open(options['pdb_seqres_file']) as f:
            for line in f:
                if line.startswith('>'):
                    data, annotation = line[1:].rstrip().split('  ', 1)
                    pdb_chain, mol_type, other = data.split(' ', 2)
                    if mol_type != 'mol:protein':
                        continue
                    pdb_id, chain = pdb_chain.split('_', 1)
                    print(
                        'Inserting annotation for %s (%s)' % (pdb_chain,
                                                              annotation
                                                              )
                        )
                    pdb_obj, created = databases_models.PDB\
                        .objects.update_or_create(id=pdb_id)
                    annotation_obj, created = databases_models.PDBAnnotation\
                        .objects.update_or_create(annotation=annotation)
                    databases_models.Chain.objects.update_or_create(
                        pdb=pdb_obj, chain=chain,
                        defaults={'annotation': annotation_obj}
                        )

