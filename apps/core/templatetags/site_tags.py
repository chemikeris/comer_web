from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def help_link():
    link = '<a href="' + reverse('help') + '">Help page</a>'
    return mark_safe(link)

