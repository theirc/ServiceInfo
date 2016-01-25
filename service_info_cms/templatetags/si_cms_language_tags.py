from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def service_language_code(context, service):
    request = context['request']
    return settings.SERVICE_LANGUAGE_CODES[service.lower()][request.LANGUAGE_CODE]


@register.simple_tag
def menu_language_name(language_code):
    return settings.MENU_LANGUAGE_NAMES[language_code]
