from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def help_tooltip_questionmark(help_id):
    help_questionmark = \
        ' (<a href="#" data-bs-toggle="collapse" data-bs-target="#' + \
        help_id + \
        '">?</a>)'
    return mark_safe(help_questionmark)


@register.filter
@stringfilter
def help_tooltip(help_id, text):
    help_tooltip_html = \
        f'<div id="{help_id}" class="help_tooltip collapse">'\
        f'<p class="bg-info border border-secondary rounded p-1">'\
        f'{text}</p></div>'
    return mark_safe(help_tooltip_html)

