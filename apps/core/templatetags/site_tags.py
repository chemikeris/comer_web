from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def help_link():
    link = '<a href="' + reverse('help') + '">Help page</a>'
    return mark_safe(link)


@register.filter
@stringfilter
def github_link(github_uri, link_text=None):
    if link_text is None:
        link_text = 'GitHub'
    link = f'<a href="https://github.com/{github_uri}">{link_text}</a>'
    return mark_safe(link)

