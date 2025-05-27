import os
import json
import logging
import re

from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.databases import models as databases_models

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
    if filter_key is None or json_error:
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


def standard_result_name(name):
    "Convert results to standard IDs, mostly for UniProt"
    if name.startswith('sp|'):
        # This is SwissProt, getting UniProt AC from it.
        standard_name = name.split('|')[1]
    elif name.startswith('AF-'):
        # This is AlphaFold DB, getting UniProt AC from it.
        standard_name = name.split('-')[1]
    elif name.startswith('ECOD'):
        standard_name = name.split('_')[-1]
    else:
        # All other databases have only one representation.
        standard_name = name
    return standard_name


def is_Pfam_result(name):
    "Check if the result is a Pfam result"
    if name.startswith('PF'):
        return True
    else:
        return False


def is_CDD_result(name):
    "Check if the result is a Pfam result"
    if name.startswith('cd'):
        return True
    else:
        return False


def is_COG_KOG_result(name):
    "Check if the result is a Pfam result"
    if name.startswith('COG'):
        return True
    elif name.startswith('KOG'):
        return True
    else:
        return False


def suitable_for_structure_modeling(name):
    if is_Pfam_result(name):
        return False
    elif is_CDD_result(name):
        return False
    elif is_COG_KOG_result(name):
        return False
    else:
        return True


def get_object_or_404_for_removed_also(model, **kwargs):
    "Wrapper for get_object_or_404 that gives error 404 for removed jobs"
    m = get_object_or_404(model, **kwargs)
    if m.status == m.REMOVED:
        raise Http404
    else:
        return m


def format_gtalign_description(description, get_annotation=False):
    "Parse description from GTalign JSON"
    def trim_id(i):
        if i.endswith('.cif.gz'):
            return i.split('.')[0]
        elif i.endswith('.pdb.gz'):
            return i.split('.')[0]
        elif i.endswith('.ent'):
            return i.split('.')[0]
        elif i.endswith('.tar'):
            return i.split('.')[0]
        else:
            return i
    def afdb_id_to_uniprot(i):
        uniprot_ac = i.split('-')[1]
        return uniprot_ac
    def ecod_identifier_to_domain_name(i, get_annotation):
        ecod_uid = after_colon(i).split('.')[0]
        ecod_data = databases_models.ECOD.objects.filter(uid=int(ecod_uid))[0]
        if get_annotation:
            annotation_parts = []
            if ecod_data.pdb_chain:
                if ecod_data.pdb_chain.annotation:
                    pdb_annotation = ecod_data.pdb_chain.annotation.annotation
                    annotation_parts.append('Protein: %s' % pdb_annotation)
                else:
                    pdb_annotation = ''
            else:
                pdb_annotation = ''
            ecod_names = {}
            for d in ecod_data.annotations.all():
                ecod_names[d.get_ecod_hierarchy_display()] = d.name
            for h in ('A', 'X', 'H', 'T', 'F'):
                try:
                    if ecod_names[h]:
                        annotation_parts.append('%s: %s' % (h, ecod_names[h]))
                except KeyError:
                    pass
            return ecod_data.ecod_domain_id, ', '.join(annotation_parts)
        else:
            return ecod_data.ecod_domain_id
    def after_colon(i):
        return i.split(':')[1]
    def get_uniprot_annotation(uniprot_ac):
        uniprot_entries = databases_models.UniProt.objects.filter(
            uniprot_ac=uniprot_ac
            )
        if len(uniprot_entries) == 0:
            return ''
        else:
            return uniprot_entries[0].annotation
    # Specific functions end here, and processing begins.
    parts = split_gtalign_description(description)
    identifier = os.path.basename(parts[0])
    if identifier.startswith('ecod'):
        if get_annotation:
            ecod_domain_name, annotation = ecod_identifier_to_domain_name(
                identifier, True)
            return ecod_domain_name, annotation
        else:
            ecod_domain_name = ecod_identifier_to_domain_name(identifier,
                                                              False)
            return ecod_domain_name
    elif identifier.startswith('scope'):
        identifier = trim_id(after_colon(identifier))
        if get_annotation:
            scop_entries = databases_models.SCOP.objects.filter(
                domain_id=identifier)
            if scop_entries:
                annotation = scop_entries[0].annotation
            else:
                annotation = ''
            return identifier, annotation
        else:
            return identifier
    elif identifier.startswith('swissprot') or identifier.startswith('uniref'):
        uniprot_ac = afdb_id_to_uniprot(after_colon(identifier))
        if get_annotation:
            annotation = get_uniprot_annotation(uniprot_ac)
            return uniprot_ac, annotation
        else:
            return uniprot_ac
    elif identifier.startswith('UP'):
        id_parts = identifier.split(':')
        identifier = afdb_id_to_uniprot(id_parts[1])
        proteomes_identifier = '%s %s' % (identifier, trim_id(id_parts[0]))
        if get_annotation:
            annotation = get_uniprot_annotation(identifier)
            return proteomes_identifier, annotation
        else:
            return proteomes_identifier
    else:
        # Assuming PDB here
        if ':' in identifier:
            identifier = identifier.split(':')[1]
        identifier = trim_id(identifier)
        chain = parts[1]
        model = parts[2]
        pdb_identifier_to_show = '%s_%s_%s' % (identifier, chain, model)
        if get_annotation:
            pdb_entries = databases_models.Chain.objects.filter(
                pdb_id=identifier, chain=chain)
            if len(pdb_entries) == 0:
                annotation = ''
            else:
                pdb_entry = pdb_entries[0]
                annotation_data = pdb_entry.annotation
                if annotation_data is None:
                    annotation = ''
                else:
                    annotation = annotation_data.annotation
            return pdb_identifier_to_show, annotation
        else:
            return pdb_identifier_to_show


def correct_structure_file_path(
        description, old_dir, new_dir, tar_replacement=None
        ):
    parts = split_gtalign_description(description)
    remote_path = parts[0]
    chain = parts[1]
    model = parts[2]
    local_path = remote_path.replace(old_dir, new_dir)
    if tar_replacement:
        local_path = local_path.replace(tar_replacement[0], tar_replacement[1])
    output = {'file': local_path, 'chain': chain, 'model': model}
    return output


def split_gtalign_description(description):
    "Split description from GTalign JSON to parts"
    m = re.search(
        r'\s*(Chn\:([^"\s\)]+))?(\s+\(M\:([^"\s\)]+)\))?$',
        description
        )
    # Should match the "string Chn:A (M:1)" pattern where Chn and M parts are
    # optional.
    path = description[0:m.span()[0]]
    chain = m.group(2)
    model_group = m.group(4)
    model = 1 if model_group is None else int(model_group)
    return path, chain, model

