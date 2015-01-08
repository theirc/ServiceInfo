import os

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

import api.urls

# FIXME: Developers, remove this once we have any real translated strings.
# There has to be one string or none of the tools produce any output, which
# is confusing.
# Translators: You do NOT need to translate this:
foo = _("THIS IS A TEST")

FRONTEND_DIR = os.path.join(settings.PROJECT_ROOT, 'frontend')

# Reminder: the `static` function is a no-op if DEBUG is False, as in production.
urlpatterns = [
    # Django admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # Redirect / to /index.html if running locally.
        url(r'^$', RedirectView.as_view(url=settings.STATIC_URL + 'index.html'), name='index-html-redirect'),
    ]
