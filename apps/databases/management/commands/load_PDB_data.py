from django.core.management.base import BaseCommand, CommandError

from apps.databases import models as databases_models


class Command(BaseCommand):
    help = 'Load PDB data from a locally downloaded PDB SEQRES file'
    # PDB SEQRES file url: 
    # https://files.wwpdb.org/pub/pdb/derived_data/pdb_seqres.txt
    #
    # PDB entries file url:
    # https://files.rcsb.org/pub/pdb/derived_data/index/entries.idx

    def add_arguments(self, parser):
        parser.add_argument('--pdb-seqres-file', help="PDB SEQRES file")
        parser.add_argument('--pdb-entries-file', help="PDB entries file")

    def handle(self, *args, **options):
        if options['pdb_entries_file']:
            print('Loading PDB entry titles.')
            parsing = False
            with open(options['pdb_entries_file']) as f:
                for line in f:
                    if parsing:
                        load_PDB_titles_from_entries_file(line)
                    else:
                        if line.startswith('----'):
                            parsing = True
                        continue
        if options['pdb_seqres_file']:
            print('Loading PDB chain annotations.')
            with open(options['pdb_seqres_file']) as f:
                for line in f:
                    if line.startswith('>'):
                        load_PDB_chain_annotation_from_seqres(line)


def load_PDB_titles_from_entries_file(entries_file_line):
    "Load PDB entry annotation to DB"
    parts = entries_file_line.rstrip().split('\t')
    pdb_id = parts[0].lower()
    title = parts[3]
    print(f'PDB entry {pdb_id}, title: {title}')
    pdb_obj, created = databases_models.PDB.objects.update_or_create(
        id=pdb_id, defaults={'title': title}
        )


def load_PDB_chain_annotation_from_seqres(seqres_fasta_header_line):
    "Load PDB chain annotation to database"
    data, annotation = seqres_fasta_header_line[1:].rstrip().split('  ', 1)
    pdb_chain, mol_type, other = data.split(' ', 2)
    pdb_id, chain = pdb_chain.split('_', 1)
    print('Inserting annotation for %s (%s)' % (pdb_chain, annotation))
    pdb_obj, created = databases_models.PDB.objects.update_or_create(id=pdb_id)
    annotation_obj, created = databases_models.PDBAnnotation\
        .objects.update_or_create(annotation=annotation)
    databases_models.Chain.objects.update_or_create(
        pdb=pdb_obj, chain=chain,
        defaults={'annotation': annotation_obj}
        )

