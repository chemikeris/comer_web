from django import forms
from django.core.exceptions import ValidationError

from apps.core.models import get_databases_for
from apps.core.utils import search_input_files_exist
from . import default


MAX_STRUCTURE_TEXT_INPUT = 5242880
MAX_INPUT_FILE_SIZE_IN_MB = 50


# Code below is from Django documentation
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
##


class StructureInputForm(forms.Form):
    structure = forms.CharField(
        max_length=MAX_STRUCTURE_TEXT_INPUT, required=False,
        label='Paste structure', widget=forms.Textarea
        )
    input_query_files = MultipleFileField(
        required=False, label='Upload structure file(s)'
        )
    database = forms.ChoiceField(
        choices=get_databases_for('gtalign'),
        initial=get_databases_for('gtalign', ['pdb_mmcif']),
        label='Database'
        )
    email = forms.EmailField(required=False, label='E-mail (optional)')
    description = forms.CharField(
        required=False, label='Custom job description (optional)', max_length=140
        )
    # GTalign settings
    s = forms.FloatField(
        min_value=0, max_value=1, label='TM-score threshold',
        initial=default.settings['s']
        )
    s.widget.attrs.update({'step': 0.01})
    sort = forms.ChoiceField(
        label='Sort options',
        choices=(
            (0, 'Sort results by the greater TM-score of the two',),
            (1, 'Sort by reference length-normalized TM-score',),
            (2, 'Sort by query length-normalized TM-score',),
            (3, 'Sort by the harmonic mean of the two TM-scores',),
            (4, 'Sort by RMSD',),
            (5, 'Sort by the greater 2TM-score',),
            (6, 'Sort by reference length-normalized 2TM-score',),
            (7, 'Sort by query length-normalized 2TM-score',),
            (8, 'Sort by the harmonic mean of the 2TM-scores',),
            ),
        initial=2
        )
    nhits = forms.IntegerField(
        label='Number of results',
        min_value=1, max_value=1000,
        initial=default.settings['nhits']
        )
    nalns = forms.IntegerField(
        label='Number of structure alignments',
        min_value=1, max_value=1000,
        initial=default.settings['nalns']
        )
    presimilarity = forms.FloatField(
        label='Sequence similarity pre-screening threshold',
        min_value=0,
        initial=default.settings['pre-similarity']
        )
    prescore = forms.FloatField(
        label='Minimal provisional TM-score',
        min_value=0, max_value=1,
        initial=default.settings['pre-score']
        )
    speed = forms.IntegerField(
        label='GTalign algorithm speed',
        min_value=0, max_value=13,
        initial=default.settings['speed']
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data['structure'] and not self.files:
            raise ValidationError('No query structure input!')
        structure_lines = cleaned_data['structure'].splitlines()
        cleaned_data['structure'] = '\n'.join(structure_lines)+'\n'


