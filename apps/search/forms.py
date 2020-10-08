from django import forms
from django.conf import settings

class BaseInputForm(forms.Form):
    "COMER search input form"
    # Input sequence.
    sequence = forms.CharField(widget=forms.Textarea)
    # Database to search.
    database = forms.ChoiceField(choices=settings.SEQUENCE_DATABASES)
    # Optional job name and email fields.
    # job_name = forms.CharField(required=False, label='Job name (optional)')
    # Custom job name field to be introduced in the future.
    email = forms.EmailField(required=False, label='E-mail (optional)')
    # Output options.
    EVAL = forms.FloatField(min_value=0, max_value=10, label='E-value')
    NOHITS = forms.IntegerField(label='Number of hits')
    NOALNS = forms.IntegerField(label='Number of alignments')
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
            ('0', 'significance depends on profile lengths'),
            ('1', 'significance depends on profile attributes and compositional similarity'),
            ('2', 'significance depents on profile lengths but regards the amount of data used in simulations'),
            )
        )
    # Alignment options.
    MAPALN = forms.BooleanField(label='Realign by a maximum a posteriori algorithm')
    MINPP = forms.FloatField(
        min_value=0, max_value=1, label='Posterior probability threshold'
        )


class SequencesInputForm(BaseInputForm):
    "Input form for sequences"
    msa_input = forms.BooleanField(
        widget=forms.HiddenInput(), initial=False, required=False
        )


class MultipleAlignmentInputForm(BaseInputForm):
    "Input form for sequences"
    msa_input = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

