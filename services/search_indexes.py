from aldryn_search.utils import get_index_base

from .models import Service


class ServiceIndex(get_index_base()):
    haystack_use_for_indexing = True
    index_title = True

    def get_title(self, obj):
        return obj.name

    def get_index_queryset(self, language):
        # For this language's index, don't include services with no name
        # provided in this language.
        return Service.objects.filter(status=Service.STATUS_CURRENT).exclude(**{
            'name_%s' % language: ''
        })

    def get_model(self):
        return Service

    def get_search_data(self, service, language, request):
        description = getattr(service, 'description_%s' % language, '')
        additional_info = getattr(service, 'additional_info_%s' % language, '')
        return ' '.join((
            service.provider.name,
            service.name,
            service.area_of_service.name,
            description,
            additional_info,
            service.type.name,
        ))
