from django.contrib import admin
from services.models import Provider, Service, ServiceArea, SelectionCriterion, ProviderType


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr', 'type']


class ProviderTypeAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr']


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr', 'provider', 'area_of_service']
    list_display_links = ['name_en', 'name_ar', 'name_fr', 'provider', 'area_of_service']


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderType, ProviderTypeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceArea)
admin.site.register(SelectionCriterion)
