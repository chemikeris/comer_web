from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError


class SequenceField(forms.CharField):
    "Sequence input field"
    def to_python(self, value):
        input_str = super().to_python(value)
        # Normalizing newlines, always '\n' in further processing.
        input_str = '\n'.join(input_str.splitlines())
        if input_str.startswith('>'):
            seq_format = 'fasta'
            sequences_data = input_str
        elif input_str.startswith('# STOCKHOLM'):
            seq_format = 'stockholm'
            first_line, sequences_data = input_str.split('\n', 1)
        else:
            seq_format = 'plain'
            sequences_data = input_str
        return (sequences_data, seq_format)


class BaseInputForm(forms.Form):
    "COMER search input form"
    # Input sequence.
    sequence = SequenceField(widget=forms.Textarea, strip=True)
    # Database to search.
    database = forms.ChoiceField(choices=settings.SEQUENCE_DATABASES)
    # Optional job name and email fields.
    # job_name = forms.CharField(required=False, label='Job name (optional)')
    # Custom job name field to be introduced in the future.
    email = forms.EmailField(required=False, label='E-mail (optional)')
    # Output options.
    EVAL = forms.FloatField(min_value=0, max_value=10, label='E-value')
    # Number of results that will be converted to number of hits and number of
    # alignments.
    number_of_results = forms.IntegerField(
        label='Number of results',  min_value=1
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

    def validate_sequence(self, sequence_str, description):
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

    def validate_fasta(self, fasta_str, check_length=False):
        "Validate fasta input"
        sequences_data = fasta_str[1:].split('\n>')
        sequences = []
        for s in sequences_data:
            description, sequence = s.split('\n', 1)
            d = description + sequence
            sequence = self.validate_sequence(sequence, description)
            if sequence:
                sequences.append((description, sequence))
        if check_length:
            first_sequence_length = len(sequences[0][1])
            for unused_description, sequence in sequences:
                if len(sequence) != first_sequence_length:
                    msg = 'Lengths of sequences in alignments are not equal!'
                    self.add_error('sequence', ValidationError(msg))
        return sequences


class SequencesInputForm(BaseInputForm):
    "Input form for sequences"
    msa_input = forms.BooleanField(
        widget=forms.HiddenInput(), initial=False, required=False
        )

    def clean_sequence(self):
        "Clean single sequence input"
        sequences_data, seq_format = self.cleaned_data['sequence']
        if seq_format == 'plain':
            sequences = (self.validate_sequence(sequences_data, None),)
        elif seq_format == 'fasta':
            sequences = self.validate_fasta(sequences_data)
        elif seq_format == 'stockholm':
            raise ValidationError(
                'Sequence input does not accept Stockholm format!'
                )
        else:
            raise ValidationError('Unknown input format!')
        return sequences, seq_format


class MultipleAlignmentInputForm(BaseInputForm):
    "Input form for sequences"
    msa_input = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    def clean_sequence(self):
        "Clean single sequence input"
        sequences_data, seq_format = self.cleaned_data['sequence']
        if seq_format == 'plain':
            raise ValidationError(
                'MSA input does not accept plain text format!'
                )
        elif seq_format == 'fasta':
            alignments_data = sequences_data.split('\n//\n')
            alignments = []
            for a in alignments_data:
                alignment = self.validate_fasta(a, check_length=True)
                if alignment:
                    alignments.append(alignment)
        elif seq_format == 'stockholm':
            alignments = sequences_data.rstrip().split('\n//\n')
            # Cleaning last '//' from the last alignment
            alignments[-1] = alignments[-1][:-3]
        else:
            raise ValidationError('Unknown input format!')
        return alignments, seq_format

