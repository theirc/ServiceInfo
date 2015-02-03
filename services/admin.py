from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from services.models import Provider, Service, ServiceArea, SelectionCriterion, ProviderType, \
    ServiceType


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr', 'type']


class ProviderTypeAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr']


class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['number',
                    'name_en', 'name_ar', 'name_fr',
                    'comments_en', 'comments_ar', 'comments_ar']


class ServiceAdmin(admin.ModelAdmin):
    actions = ['approve', 'reject']
    fieldsets = (
        (None, {
            'fields': [
                'provider',
                ('status', 'type'),
                ('name_en', 'name_ar', 'name_fr'),
                'area_of_service',
                'cost_of_service',
                'update_of',
                ],
        }),
        (_('Description and Additional Information'), {
            'classes': ('collapse',),
            'fields': [
                'description_en',
                'description_ar',
                'description_fr',
                'additional_info_en',
                'additional_info_ar',
                'additional_info_fr',
            ]
        }),
        (_('Hours'), {
            'classes': ('collapse',),
            'fields': [
                ('sunday_open', 'sunday_close',),
                ('monday_open', 'monday_close',),
                ('tuesday_open', 'tuesday_close',),
                ('wednesday_open', 'wednesday_close',),
                ('thursday_open', 'thursday_close',),
                ('friday_open', 'friday_close',),
                ('saturday_open', 'saturday_close',),
            ]
        }),
        (_('Location'), {
            'classes': ('collapse',),
            'fields': ['location'],
        }),
        (_('Selection criteria'), {
            'classes': ('collapse',),
            'fields': ['selection_criteria'],
        })
    )
    filter_horizontal = ['selection_criteria']
    list_display = ['name_en', 'name_ar', 'name_fr',
                    'provider',
                    'type',
                    'status',
                    'area_of_service',
                    ]
    list_display_links = ['name_en', 'name_ar', 'name_fr', 'provider', 'area_of_service']
    list_filter = ['status', 'type']
    readonly_fields = ['provider', 'update_of', 'status']

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "selection_criteria":
            # We'd like to only show selection criteria already attached to services
            # owned by the same user who owns the service currently being edited.
            # Unfortunately the only thing we have access to here that has data
            # for the current request is the request object...
            # For now, just leave this to fix later.
            pass
            # kwargs["queryset"] = \
            #     SelectionCriterion.objects.filter(services__provider__user=service.provider.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def approve(self, request, queryset):
        # All must be in DRAFT status
        if queryset.exclude(status=Service.STATUS_DRAFT).exists():
            self.message_user(request,
                              _("Only services in draft status may be approved"),
                              messages.ERROR)
            return
        for service in queryset:
            service.staff_approve()
        self.message_user(request, _("Services have been approved"))
    approve.short_description = _("Approve new or changed service")

    def reject(self, request, queryset):
        # All must be in DRAFT status
        if queryset.exclude(status=Service.STATUS_DRAFT).exists():
            self.message_user(request,
                              _("Only services in draft status may be rejected"),
                              messages.ERROR)
            return
        for service in queryset:
            service.staff_reject()
        self.message_user(request, _("Services have been rejected"))
    reject.short_description = _("Reject new or changed service")


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderType, ProviderTypeAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceArea)
admin.site.register(SelectionCriterion)
