from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def service_language_code(context, service):
    request = context['request']
    return settings.SERVICE_LANGUAGE_CODES[service.lower()][request.LANGUAGE_CODE]
