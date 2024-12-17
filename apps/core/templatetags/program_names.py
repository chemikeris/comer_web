from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def replace_name(input_str, new_program_name):
    return input_str.replace('{PROGRAM}', new_program_name.lower())


@register.filter
@stringfilter
def add_program_if_necessary(input_str, program_name):
    program_name = program_name.lower()
    if program_name == 'gtalign':
        return '%s_%s' % (program_name, input_str)
    else:
        return input_str

