from django.contrib import admin
from services.models import Provider, Service, ServiceArea, SelectionCriterion, ProviderType


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']


class ProviderTypeAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_fr', 'name_ar']


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'area_of_service']
    list_display_links = ['name', 'provider', 'area_of_service']


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderType, ProviderTypeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceArea)
admin.site.register(SelectionCriterion)
