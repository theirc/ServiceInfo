from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

# FIXME: Developers, remove this once we have any real translated strings.
# There has to be one string or none of the tools produce any output, which
# is confusing.
# Translators: You do NOT need to translate this:
foo = _("THIS IS A TEST")


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
