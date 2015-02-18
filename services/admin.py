from django.conf import settings
from django.contrib import admin, messages
from django.contrib.gis.admin import GeoModelAdmin
from django.utils.translation import ugettext_lazy as _
from services.models import Provider, Service, ServiceArea, SelectionCriterion, ProviderType, \
    ServiceType, JiraUpdateRecord


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr', 'type']


class ProviderTypeAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'name_fr']


class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['number',
                    'name_en', 'name_ar', 'name_fr',
                    'comments_en', 'comments_ar', 'comments_ar']


class SelectionCriterionAdmin(admin.ModelAdmin):
    list_display = ['service', 'text_en', 'text_ar', 'text_fr']


class SelectionCriterionInlineAdmin(admin.TabularInline):
    model = SelectionCriterion

    # Staff can't add/delete criteria here, just edit the ones that are there:
    can_delete = False
    extra = 0
    max_num = 0
    # (Though if they're clever, they can go to the admin for selection criteria
    # and create or edit one there that links to the service.)


class ServiceAdmin(GeoModelAdmin):
    # Use CDN-hosted OpenLayers so that (1) we can use https, and (2) all the
    # images that are loaded relative to the js file will also load without
    # our having to track them all down and host them ourselves.
    openlayers_url = '//cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

    class Media:
        css = {
            "all": ("css/admin_styles.css",)
        }
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
        (_('Hours (all times in time zone {timezone})').format(timezone=settings.TIME_ZONE), {
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
    )
    inlines = [SelectionCriterionInlineAdmin]
    list_display = ['name_en', 'name_ar', 'name_fr',
                    'provider',
                    'type',
                    'status',
                    'area_of_service',
                    ]
    list_display_links = ['name_en', 'name_ar', 'name_fr', 'provider', 'area_of_service']
    list_filter = ['status', 'type']
    readonly_fields = ['provider', 'update_of', 'status']

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


class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'parent', 'name_en', 'name_ar', 'name_fr')


class JiraUpdateRecordAdmin(admin.ModelAdmin):
    list_display = ('update_type', 'service', 'provider', 'jira_issue_key')


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderType, ProviderTypeAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceArea, ServiceAreaAdmin)
admin.site.register(SelectionCriterion, SelectionCriterionAdmin)
admin.site.register(JiraUpdateRecord, JiraUpdateRecordAdmin)
