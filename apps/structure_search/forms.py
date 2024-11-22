from django import forms

from apps.core.models import get_databases_for


MAX_STRUCTURE_TEXT_INPUT = 5242880
MAX_INPUT_FILE_SIZE_IN_MB = 50

class StructureInputForm(forms.Form):
    structure = forms.CharField(
        max_length=MAX_STRUCTURE_TEXT_INPUT, required=False,
        label='Paste structure'
        )
    input_query_files = forms.FileField(
        required=False, label='Upload structure file(s)'
        )
    databases = forms.ChoiceField(
        choices=get_databases_for('gtalign'),
        initial=get_databases_for('gtalign', 'pdb'),
        label='Databases'
        )
    email = forms.EmailField(required=False, label='E-mail (optional)')
    # GTalign settings

