import logging


def format(input_str):
    "Check input format"
    if input_str.startswith('>'):
        seq_format = 'fasta'
    elif input_str.startswith('# STOCKHOLM'):
        seq_format = 'stockholm'
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

