from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import IconNameExtension, RatingExtension


class IconNameExtensionAdmin(PageExtensionAdmin):
    pass


class RatingExtensionAdmin(PageExtensionAdmin):
    pass


admin.site.register(IconNameExtension)
admin.site.register(RatingExtension)
