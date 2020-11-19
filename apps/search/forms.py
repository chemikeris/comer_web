from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError


class SequenceField(forms.CharField):
    "Sequence input field"
    def to_python(self, value):
        input_str = super().to_python(value)
        # Normalizing newlines, always '\n' in further processing.
        sequences_data = '\n'.join(input_str.splitlines())
        if input_str.startswith('>'):
            seq_format = 'fasta'
        elif input_str.startswith('# STOCKHOLM'):
            seq_format = 'stockholm'
        else:
            seq_format = 'plain'
        return (sequences_data, seq_format)


class BaseInputForm(forms.Form):
    "COMER search input form"
    # Input sequence.
    sequence = SequenceField(widget=forms.Textarea, strip=True)
    # Database to search.
    database = forms.ChoiceField(choices=settings.COMER_DATABASES)
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
        label='Number of results',  min_value=1
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
            sequence = self.validate_sequence(sequence, description)
            if sequence:
                sequences.append((description, sequence))
        if check_length:
            first_sequence_length = len(sequences[0][1])
            for unused_description, sequence in sequences:
                if len(sequence) != first_sequence_length:
                    msg = 'Lengths of sequences in alignments are not equal!'
                    self.add_error('sequence', ValidationError(msg))
        return fasta_str

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
        return sequences_data, seq_format


class MultipleAlignmentInputForm(BaseInputForm):
    "Input form for sequences"
    msa_input = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    def clean_sequence(self):
        "Clean multiple sequence alignment input"
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
        return sequences_data, seq_format

