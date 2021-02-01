from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from . import default
from . import sequences

class SequenceField(forms.CharField):
    "Sequence input field"
    def to_python(self, value):
        input_str = super().to_python(value)
        # Normalizing newlines, always '\n' in further processing.
        sequences_data = '\n'.join(input_str.splitlines()).split('\n//\n')
        return sequences_data


class SequencesInputForm(forms.Form):
    "COMER search input form"
    # Input sequence.
    sequence = SequenceField(widget=forms.Textarea, strip=True)
    # Database to search.
    comer_db = forms.ChoiceField(
        choices=settings.COMER_DATABASES, label='Database'
        )
    # Optional job name and email fields.
    # job_name = forms.CharField(required=False, label='Job name (optional)')
    # Custom job name field to be introduced in the future.
    email = forms.EmailField(required=False, label='E-mail (optional)')
    # Output options.
    EVAL = forms.FloatField(min_value=0, max_value=10, label='E-value')
    # Number of results that will be converted to number of hits and number of
    # alignments.
    number_of_results = forms.IntegerField(
        label='Number of results',  min_value=1,
        initial=default.number_of_results
        )
    # Profile generation options.
    # HHsuite.
    hhsuite_in_use = forms.BooleanField(
        label='Use HHblits for profile generation', required=False,
        )
    hhsuite_db = forms.ChoiceField(
        choices=settings.HHSUITE_DATABASES, label='HHsuite database'
        )
    hhsuite_opt_niterations = forms.IntegerField(
        label='Number of HHblits iterations', required=False
        )
    hhsuite_opt_evalue = forms.FloatField(
        label='HHblits E-value threshold', required=False
        )
    # HMMer
    hmmer_in_use = forms.BooleanField(
        label='Use hmmer for profile generation', required=False, 
        )
    sequence_db = forms.ChoiceField(
        choices = settings.SEQUENCE_DATABASES, label='hmmer database'
        )
    hmmer_opt_niterations = forms.IntegerField(
        label='Number of hmmer iterations', required=False
        )
    hmmer_opt_evalue = forms.FloatField(
        label='hmmer E-value threshold', required=False
        )

    # Profile construction options.
    ADJWGT = forms.FloatField(
        min_value=0, max_value=1, label='Weight of adjusted scores'
        )
    CVSWGT = forms.FloatField(
        min_value=0, max_value=1, label='Weight of vector scores'
        )
    SSSWGT = forms.FloatField(
        min_value=0, max_value=1, label='Weight of SS scores'
        )
    # Statistical significance estimation.
    SSEMODEL = forms.ChoiceField(
        label='Statistical significance estimation',
        choices=(
            ('0', 'depends on profile lengths'),
            ('1', 'depends on profile attributes and compositional similarity'),
            ('2', 'depends on profile lengths but regards the amount of data used in simulations'),
            )
        )
    # Alignment options.
    MAPALN = forms.BooleanField(label='Realign by a maximum a posteriori algorithm')
    MINPP = forms.FloatField(
        min_value=0, max_value=1, label='Posterior probability threshold'
        )

    def validate_plain_sequence(self, sequence_str, description):
        "Making valid sequence from input"
        # Trimming all whitespace from input string first.
        sequence_str = ''.join(sequence_str.split())
        # Allowing gaps (-) in sequence.
        sequence_to_check = sequence_str.replace('-', '')
        if sequence_to_check.isalpha():
            return sequence_str
        else:
            if description:
                msg = 'Sequence "%(desc)s" contains illegal characters!'
                params = {'desc': description}
            else:
                msg = 'Sequence contains illegal characters!'
                params = {}
            self.add_error('sequence', ValidationError(msg, params=params))
            return None

    def validate_fasta(self, input_fasta_str):
        all_sequences = sequences.split_fasta(input_fasta_str)
        if len(all_sequences) > 1:
            correct_msa = sequences.length_is_the_same(all_sequences)
            if not correct_msa:
                msg = 'Lengths of sequences in alignment are not equal!'
                self.add_error('sequence', ValidationError(msg))
        for description, sequence in all_sequences:
            sequence = self.validate_plain_sequence(sequence, description)
        return input_fasta_str

    def clean(self):
        cleaned_data = super().clean()
        # If HHsuite or HMMer is used, it's settings have to be defined.
        if cleaned_data['hhsuite_in_use']:
            if not cleaned_data['hhsuite_opt_niterations']:
                self.add_error(
                    'hhsuite_opt_niterations',
                    ValidationError(
                        'Number of HHblits iterations is required!'
                        )
                    )
            if not cleaned_data['hhsuite_opt_evalue']:
                self.add_error(
                    'hhsuite_opt_evalue',
                    'HHsuite E-value is required!'
                    )
        if cleaned_data['hmmer_in_use']:
            if not cleaned_data['hmmer_opt_niterations']:
                self.add_error(
                    'hmmer_opt_niterations',
                    ValidationError(
                        'Number of hmmer iterations is required!'
                        )
                    )
            if not cleaned_data['hmmer_opt_evalue']:
                self.add_error(
                    'hmmer_opt_evalue',
                    'hmmer E-value is required!'
                    )

    def clean_sequence(self):
        "Clean single sequence input"
        sequences_data = self.cleaned_data['sequence']
        # If no // separator is found and sequences format is fasta, it might
        # be in fact multiple sequences input that needs to be checked if it is
        # MSA, and splitted using // otherwise.
        if len(sequences_data) == 1:
            seq_format = sequences.format(sequences_data[0])
            if seq_format == 'fasta':
                all_sequences = sequences.split_fasta(sequences_data[0])
                msa_input = sequences.length_is_the_same(all_sequences)
                if msa_input:
                    pass
                else:
                    # Splitting fasta input into sequences because it is not a
                    # multiple sequence alignment.
                    new_sequences_data = []
                    for desc, seq in all_sequences:
                        new_sequences_data.append(sequences.fasta_format(desc, seq))
                    sequences_data = new_sequences_data

        cleaned_sequences_data = []
        for s in sequences_data:
            seq_format = sequences.format(s)
            if seq_format == 'stockholm':
                # Stockholm format is not validated in web server.
                cleaned_sequences_data.append(s)
            elif seq_format == 'fasta':
                cleaned_sequences_data.append(self.validate_fasta(s))
            elif seq_format == 'plain':
                cleaned_sequence = self.validate_plain_sequence(
                    s, 'plain text query'
                    )
                if cleaned_sequence:
                    cleaned_sequences_data.append(cleaned_sequence)
            else:
                raise ValidationError('Unknown input format!')
        return '\n//\n'.join(cleaned_sequences_data)

