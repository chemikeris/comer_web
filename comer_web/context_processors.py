from django.conf import settings
from django.utils.safestring import mark_safe

def google_analytics(request):
    return {'google_analytics_tag': mark_safe(settings.GOOGLE_ANALYTICS_CODE)}

