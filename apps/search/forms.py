from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from . import default
from apps.core import sequences
from apps.core.utils import search_input_files_exist

MAX_SEQUENCE_INPUT = 1048576
MAX_NUMBER_OF_SEQUENCES = 100
MAX_NUMBER_OF_SEQUENCES_FOR_COTHER = 10
MAX_FILE_SIZE_MB = 50

class SequenceField(forms.CharField):
    "Sequence input field"
    def to_python(self, value):
        input_str = super().to_python(value)
        input_size = len(input_str)
        if input_size >= MAX_SEQUENCE_INPUT:
            raise ValidationError(
                'Sequence input is too large (%s characters).' % input_size
                )
        elif input_size == 0:
            sequences_data = []
        else:
            sequences_data = process_sequences_input_str(input_str)
        return sequences_data


def process_sequences_input_str(input_str):
    # Normalizing newlines, always '\n' in further processing.
    sequences_data = '\n'.join(input_str.splitlines())
    sequences_data = sequences_data.rstrip('/').split('\n//\n')
    sequences_data = [s.strip() for s in sequences_data]
    return sequences_data


class SequencesInputForm(forms.Form):
    "COMER search input form"
    # Input sequence.
    sequence = SequenceField(
        widget=forms.Textarea, strip=True, max_length=MAX_SEQUENCE_INPUT,
        required=False, label='Query'
        )
    input_query_file = forms.FileField(
        required=False,
        label='Input file with queries'
        )
    multi_sequence_fasta = forms.BooleanField(
        label='In case of single FASTA query, treat each sequence as a separate query',
        required=False
        )
    email = forms.EmailField(required=False, label='E-mail (optional)')
    use_cother = forms.BooleanField(
        label='Perform COTHER search by threading', required=False
        )
    # Database to search.
    comer_db = forms.MultipleChoiceField(
        choices=settings.COMER_DATABASES, label='COMER databases',
        initial=settings.COMER_DATABASES[0][0]
        )
    cother_db = forms.MultipleChoiceField(
        choices=settings.COTHER_DATABASES, label='COTHER databases',
        initial=settings.COTHER_DATABASES[0][0]
        )
    # Optional job name and email fields.
    # job_name = forms.CharField(required=False, label='Job name (optional)')
    # Custom job name field to be introduced in the future.
    # Output options.
    EVAL = forms.FloatField(min_value=0, max_value=10, label='E-value')
    EVAL.widget.attrs.update({'step': 0.1})
    # Number of results that will be converted to number of hits and number of
    # alignments.
    number_of_results = forms.IntegerField(
        label='Number of hits',  min_value=1,
        initial=default.number_of_results
        )
    # Profile generation options.
    # HHsuite.
    hhsuite_in_use = forms.BooleanField(
        label='Use HHblits for sequence search', required=False,
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
    hhsuite_opt_evalue.widget.attrs.update({'step': 0.001})
    # HMMer
    hmmer_in_use = forms.BooleanField(
        label='Use HMMER for sequence search', required=False,
        )
    sequence_db = forms.ChoiceField(
        choices = settings.SEQUENCE_DATABASES, label='HMMER database'
        )
    hmmer_opt_niterations = forms.IntegerField(
        label='Number of HMMER iterations', required=False
        )
    hmmer_opt_evalue = forms.FloatField(
        label='HMMER E-value threshold', required=False
        )
    hmmer_opt_evalue.widget.attrs.update({'step': 0.001})

    # Low complexity filtering.
    LCFILTEREACH = forms.BooleanField(
        label='Invoke low-complexity filtering',
        required=False,
        initial=True
        )
    # Profile construction options.
    ADJWGT = forms.FloatField(
        min_value=0, max_value=1,
        label='Weight for the scoring term from Bayesian modeling'
        )
    ADJWGT.widget.attrs.update({'step': 0.01})
    CVSWGT = forms.FloatField(
        min_value=0, max_value=1,
        label='Weight of the term for scoring context vectors'
        )
    CVSWGT.widget.attrs.update({'step': 0.01})
    SSSWGT = forms.FloatField(
        min_value=0, max_value=1,
        label='Weight for scoring secondary structure similarity'
        )
    # Statistical significance estimation.
    SSSWGT.widget.attrs.update({'step': 0.01})
    SSEMODEL = forms.ChoiceField(
        label='Statistical significance estimation method',
        choices=(
            ('0', 'depends on profile lengths'),
            ('1', 'depends on profile attributes and compositional similarity'),
            ('2', 'depends on profile lengths but regards the amount of data used in simulations'),
            )
        )
    # Alignment options.
    MAPALN = forms.BooleanField(label='Realign by a maximum a posteriori algorithm')
    MINPP = forms.FloatField(
        min_value=0, max_value=1,
        label='Posterior probability threshold for realignment'
        )
    MINPP.widget.attrs.update({'step': 0.01})
    # Distance distribution match scores (for COTHER).
    DDMSWGT = forms.FloatField(
        required=False, min_value=0, max_value=1,
        label='Weight of distance distribution match scores'
        )
    DDMSWGT.widget.attrs.update({'step': 0.01})

    def clean_input_query_file(self):
        input_file = self.cleaned_data.get('input_query_file', False)
        if input_file:
            if input_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValidationError(
                    'Input file cannot be larger than %(mb)s MB.',
                    params={'mb': MAX_FILE_SIZE_MB}
                    )
            return input_file

    def validate_plain_sequence(self, sequence_str, description):
        "Making valid sequence from input"
        # Trimming all whitespace from input string first.
        sequence_str = ''.join(sequence_str.split())
        # Allowing gaps (-) in sequence.
        sequence_to_check = sequence_str.replace('-', '').replace('.', '')
        if sequence_to_check.isalpha():
            return sequence_str
        else:
            if description:
                msg = 'Query "%(desc)s" contains illegal characters.'
                params = {'desc': description}
            else:
                msg = 'Query contains illegal characters.'
                params = {}
            self.add_error('sequence', ValidationError(msg, params=params))
            return None

    def validate_fasta(self, input_fasta_str):
        all_sequences, problematic_sequences = sequences.split_fasta(
            input_fasta_str
            )
        for description, sequence in all_sequences:
            sequence = self.validate_plain_sequence(sequence, description)
        self.add_problematic_fasta_errors(problematic_sequences)
        return input_fasta_str

    def add_problematic_fasta_errors(self, problematic_sequences):
        for sequence in problematic_sequences:
            self.add_error(
                'sequence',
                ValidationError('Problems with FASTA input: %s' % sequence)
                )

    def add_comer_profile_errors(self, problematic_profiles):
        for profile in problematic_profiles:
            self.add_error(
                'sequence',
                ValidationError(
                    'COMER profiles cannot be used for COTHER threading.'
                    )
                )

    def add_cother_profile_errors(self, problematic_profiles):
        for profile in problematic_profiles:
            self.add_error(
                'sequence',
                ValidationError(
                    'COTHER profiles cannot be used for the COMER search.'
                    )
                )

    def clean(self):
        cleaned_data = super().clean()
        # If HHsuite or HMMer is used, it's settings have to be defined.
        def validate_sequence_search(cd, method, program):
            method_in_use_field = f'{method}_in_use'
            n_iterations_field = f'{method}_opt_niterations'
            evalue_field = f'{method}_opt_evalue'
            if cd[method_in_use_field]:
                try:
                    n_iterations = cd[n_iterations_field]
                except KeyError:
                    n_iterations = None
                if n_iterations:
                    if not (0 < int(n_iterations) < 5):
                        self.add_error(
                            n_iterations_field,
                            ValidationError(
                                f'Number of {program} iterations shoud be'
                                ' between 0 and 4.'
                                )
                            )
                else:
                    self.add_error(
                        n_iterations_field,
                        ValidationError(
                            f'Number of {program} iterations is required.'
                            )
                        )
                evalue = cd[evalue_field]
                if evalue:
                    if not (0 <= evalue <= 1):
                        self.add_error(
                            evalue_field,
                            ValidationError(
                                f'Sequence search Evalue threshold should be'
                                ' between 0 and 1.'
                                )
                            )

                else:
                    self.add_error(
                        evalue_field,
                        ValidationError(
                            f'{program} E-value is required.'
                            )
                        )
        validate_sequence_search(cleaned_data, 'hhsuite', 'HHblits')
        validate_sequence_search(cleaned_data, 'hmmer', 'HMMER')
        # Using file input or text input?
        query_file, parameters_file = search_input_files_exist(self.files)
        sequences_data = []
        if cleaned_data['sequence']:
            sequences_data += cleaned_data['sequence']
        if query_file:
            sequences_data += process_sequences_input_str(
                query_file.read().decode()
                )
        if not sequences_data:
            raise ValidationError(
                'Please provide query in the text field or file with queries.'
                )

        # Clean sequence input (if no file was present)
        try:
            multi_sequence_fasta = cleaned_data.pop('multi_sequence_fasta')
        except KeyError:
            multi_sequence_fasta = False
        # If no // separator is found and sequences format is fasta, it might
        # be in fact multiple sequences input that needs to be checked if it is
        # MSA, and splitted using // otherwise.
        if len(sequences_data) == 1:
            seq_format = sequences.format(sequences_data[0])
            if seq_format == 'fasta' and multi_sequence_fasta:
                all_sequences, problematic_sequences = sequences.split_fasta(
                    sequences_data[0]
                    )
                self.add_problematic_fasta_errors(problematic_sequences)
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

        cother_job = cleaned_data['use_cother']
        if cother_job:
            max_no_of_sequences = MAX_NUMBER_OF_SEQUENCES_FOR_COTHER
        else:
            max_no_of_sequences = MAX_NUMBER_OF_SEQUENCES
        if len(sequences_data) > max_no_of_sequences:
            raise ValidationError(
                'Number of queries is too big, maximum %(max)s is allowed.',
                params={'max': max_no_of_sequences}
                )
        cleaned_sequences_data = []
        problematic_comer_profiles = []
        problematic_cother_profiles = []
        for i, s in enumerate(sequences_data):
            seq_format = sequences.format(s)
            if seq_format in ('stockholm', 'a3m'):
                # These formats are not validated in web server.
                cleaned_sequences_data.append(s)
            elif seq_format == 'comer':
                if cleaned_data['use_cother']:
                    # COTHER cannot use COMER profiles.
                    problematic_comer_profiles.append(s)
                else:
                    cleaned_sequences_data.append(s)
            elif seq_format == 'cother':
                if cleaned_data['use_cother']:
                    cleaned_sequences_data.append(s)
                else:
                    # COMER cannot use COTHER profiles.
                    problematic_cother_profiles.append(s)
            elif seq_format == 'fasta':
                cleaned_sequences_data.append(self.validate_fasta(s))
            elif seq_format == 'plain':
                cleaned_sequence = self.validate_plain_sequence(
                    s, 'sequence%s' % i
                    )
                if cleaned_sequence:
                    cleaned_sequences_data.append(cleaned_sequence)
            else:
                raise ValidationError('Unknown input format.')
        self.add_comer_profile_errors(problematic_comer_profiles)
        self.add_cother_profile_errors(problematic_cother_profiles)
        cleaned_data['sequence'] = cleaned_sequences_data


class SequencesInputFormWithAllSettings(SequencesInputForm):
    input_search_parameters_file = forms.FileField(required=False)
    # Output options.
    SHOW = forms.BooleanField(required=False)
    DSCLEN = forms.IntegerField(required=False)
    DSCWIDTH = forms.IntegerField(
        required=False, min_value=40, max_value=10000
        )
    ALNWIDTH = forms.IntegerField(
        required=False, min_value=20, max_value=10000
        )
    # Profile construction options.
    X_UNINF = forms.BooleanField(required=False)
    IDENTITY = forms.IntegerField(required=False, min_value=1, max_value=100)
    SHOWCMD = forms.BooleanField(required=False)
    # Advanced options.
    PCFWEIGHT = forms.FloatField(required=False)
    MINALNFRN = forms.IntegerField(required=False, min_value=1, max_value=100)
    MINALNPOS = forms.IntegerField(required=False)
    matrices = ('Blosum80', 'Blosum62', 'Blosum45', 'Pscores', 'Gonnet')
    SUBMAT = forms.ChoiceField(required=False, choices=zip(matrices, matrices))
    # Position=specific distance distribution options.
    DSTSEGM = forms.IntegerField(required=False, min_value=1, max_value=20)
    DSTPOS = forms.IntegerField(required=False, min_value=1, max_value=20)
    DSTSEP6 = forms.IntegerField(required=False, min_value=1, max_value=64)
    DSTGAPL = forms.IntegerField(required=False, min_value=1, max_value=255)
    DSTFREE = forms.IntegerField(required=False, min_value=1, max_value=20)
    # Cluster data usage options.
    score_adjustments = ('hdpctx', 'hdpsco', 'no')
    SCOADJ = forms.ChoiceField(
        required=False,
        choices=zip(score_adjustments, score_adjustments)
        )
    SUPCLT = forms.IntegerField(required=False, min_value=-1)
    cADJWGT = forms.FloatField(required=False, min_value=0, max_value=1)
    # SEG options.
    HCFILTER = forms.BooleanField(required=False)
    HCWINDOW = forms.IntegerField(required=False)
    HCLOWENT = forms.FloatField(required=False)
    HCHIGHENT = forms.FloatField(required=False)
    INVLCFILTER = forms.BooleanField(required=False)
    LCWINDOW = forms.IntegerField(required=False)
    LCLOWENT = forms.FloatField(required=False)
    LCHIGHENT = forms.FloatField(required=False)
    DISTANCE = forms.FloatField(required=False)

