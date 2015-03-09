from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.gis.admin import GeoModelAdmin
from django.contrib.gis.forms import OSMWidget
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from services.models import Provider, Service, ServiceArea, SelectionCriterion, ProviderType, \
    ServiceType, JiraUpdateRecord
from services.utils import validation_error_as_text


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


class OurOSMWidget(OSMWidget):
    # Use our own template that actually respects 'default_zoom'
    template_name = 'admin/osm-map.html'

    # Use CDN for openlayers, and http or https as appropriate.
    class Media:
        extend = False  # We want to replace OSMWidget's media, not add to it
        js = (
            '//cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js',
            '//www.openstreetmap.org/openlayers/OpenStreetMap.js',
            'gis/js/OLMapWidget.js',
        )


    # The GeoModelAdmin.get_map_widget will subclass this widget class
    # and put a lot of config into an attribute 'params'. But the render
    # method of OSMWidget never looks at 'params'... Sigh.
    def render(self, name, value, attrs=None):
        if attrs:
            self.params.update(attrs)
        return super().render(name, value, attrs=self.params)

    # The __init__ of OSMWidget does some messing around with
    # its attrs and args for default_lon and default_lat. I don't
    # feel like trying to figure that out, so just bypass it.
    def __init__(self, attrs=None):
        # Yes, we are deliberately NOT invoking OSMWidget's own __init__
        super(OSMWidget, self).__init__(attrs)


class ServiceAdmin(GeoModelAdmin):
    # https://docs.djangoproject.com/en/1.7/ref/contrib/gis/admin/#geomodeladmin

    # Use CDN-hosted OpenLayers so that (1) we can use https, and (2) all the
    # images that are loaded relative to the js file will also load without
    # our having to track them all down and host them ourselves.
    openlayers_url = '//cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

    # layers
    # basic: base map
    # clabel: country names
    # Others?   who knows but they seem like a good idea
    wms_layer = 'basic,clabel,ctylabel,statelabel,stateboundary'

    widget = OurOSMWidget  # Our subclassed OpenStreetMaps widget

    # Beirut: lat 33.8869, long 35.5131.
    default_lat = 33.8869
    default_lon = 35.5131
    default_zoom = 12

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
        any_approved = False
        for service in queryset:
            try:
                service.staff_approve()
            except ValidationError as e:
                msg = _("Unable to approve service '{name}': {error}.")
                msg = msg.format(name=service.name, error=validation_error_as_text(e))
                messages.error(request, msg)
            else:
                any_approved = True
        if any_approved:
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

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if '_approve' in request.POST:
            try:
                obj.staff_approve()
            except ValidationError as e:
                msg = _("Unable to approve service '{name}': {error}.").format(name=obj.name)
                msg = msg.format(name=obj.name, error=validation_error_as_text(e))
                self.message_user(request, msg, messages.ERROR)
                redirect_url = add_preserved_filters(
                    {'preserved_filters': self.get_preserved_filters(request),
                     'opts': self.model._meta},
                    request.path)
                return HttpResponseRedirect(redirect_url)
            else:
                msg = _('The service was approved successfully.')
                self.message_user(request, msg, messages.SUCCESS)
        elif '_reject' in request.POST:
            obj.staff_reject()
            msg = _('The service was rejected successfully.')
            self.message_user(request, msg, messages.INFO)
        return super().response_change(request, obj)


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
