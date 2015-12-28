from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import IconNameExtension


class IconNameExtensionAdmin(PageExtensionAdmin):
    pass

admin.site.register(IconNameExtension, IconNameExtensionAdmin)
