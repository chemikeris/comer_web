from django.conf import settings
from django.utils.safestring import mark_safe

def google_analytics(request):
    return {'google_analytics_tag': mark_safe(settings.GOOGLE_ANALYTICS_CODE)}


def program_info(request):
    gtalign_server = 'gtalign' in request.path
    if gtalign_server:
        base_context = {
            'program': 'GTalign',
            'sequence_search': False,
            'structure_search': True,
            }
    else:
         base_context = {
            'program': 'COMER',
            'sequence_search': True,
            'structure_search': False,
            }
    return base_context   
