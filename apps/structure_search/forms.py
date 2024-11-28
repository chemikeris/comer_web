from django import forms

from apps.core.models import get_databases_for


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
        label='Paste structure'
        )
    input_query_files = MultipleFileField(
        required=False, label='Upload structure file(s)'
        )
    databases = forms.ChoiceField(
        choices=get_databases_for('gtalign'),
        initial=get_databases_for('gtalign', 'pdb'),
        label='Databases'
        )
    email = forms.EmailField(required=False, label='E-mail (optional)')
    description = forms.CharField(
        required=False, label='Custom job description (optional)', max_length=140
        )
    # GTalign settings

