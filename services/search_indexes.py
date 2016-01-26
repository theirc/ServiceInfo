from aldryn_search.utils import get_index_base

from .models import Service


class ServiceIndex(get_index_base()):
    haystack_use_for_indexing = True
    index_title = True

    def get_title(self, obj):
        # XXX what about language?  concatenate all available languages?
        return obj.name_en

    def get_index_queryset(self, language):
        # XXX exclude objects with blank name for the selected language, not simply for EN
        return Service.objects.filter(status=Service.STATUS_CURRENT).exclude(name_en='')

    def get_model(self):
        return Service

    def get_search_data(self, service, language, request):
        # XXX return data for the selected language, not simply for EN
        return ' '.join((
            service.provider.name_en,
            service.name_en,
            service.area_of_service.name_en,
            service.description_en,
            service.additional_info_en,
            service.type.name_en,
        ))
