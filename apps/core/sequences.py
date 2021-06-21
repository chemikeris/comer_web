import logging


def format(input_str):
    "Check input format"
    if input_str.startswith('>'):
        seq_format = 'fasta'
    elif input_str.startswith('#A3M'):
        seq_format = 'a3m'
    elif input_str.startswith('# STOCKHOLM'):
        seq_format = 'stockholm'
    elif input_str.startswith('COMER'):
        seq_format = 'comer'
    else:
        seq_format = 'plain'
    return seq_format


def split_fasta(fasta_str):
    sequences_data = fasta_str[1:].split('\n>')
    sequences = []
    problematic_sequences = []
    for s in sequences_data:
        try:
            description, sequence = s.split('\n', 1)
        except:
            logging.error('Error parsing FASTA: %s', s)
            problematic_sequences.append(s)
            continue
        sequence = ''.join(sequence.split())
        sequences.append((description, sequence))
    return sequences, problematic_sequences


def fasta_format(description, sequence):
    output = ''
    output += f'>{description}\n'
    output += sequence
    return output


def length_is_the_same(sequences):
    "Check if lenght is the same among splitted fasta sequences"
    first_sequence_length = len(sequences[0][1])
    all_lengths_equal = True
    for unused_description, sequence in sequences:
        if len(sequence) != first_sequence_length:
            all_lengths_equal = False
            break
    return all_lengths_equal


def hit_alignment_starts_and_ends(hit_alignment):
    "Get positions where alignment starts on query and target sequences"
    query_starts = hit_alignment['query_from']
    query_ends = hit_alignment['query_to']
    target_starts = hit_alignment['target_from']
    target_ends = hit_alignment['target_to']
    return query_starts, query_ends, target_starts, target_ends


def alignment_description(description, starts, ends):
    "Create alignment description for COMER results processing"
    return '%s (ALN:%s-%s)' % (description, starts, ends)


def comer_json_hit_record_to_alignment(query_description, hit_record_json):
    "Convert COMER results JSON (parsed into Python format) to FASTA"
    aligned_query = hit_record_json['alignment']['query_aln']
    target_description = hit_record_json['target_description']
    aligned_target = hit_record_json['alignment']['target_aln']

    query_starts, query_ends, target_starts, target_ends = \
        hit_alignment_starts_and_ends(hit_record_json['alignment'])

    query_fasta = fasta_format(
        alignment_description(query_description, query_starts, query_ends),
        aligned_query
        )
    target_fasta = fasta_format(
        alignment_description(target_description, target_starts, target_ends),
        aligned_target
        )
    return '%s\n%s' % (query_fasta, target_fasta)

