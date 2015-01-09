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
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # Redirect / to /index.html if running locally.
        url(r'^$', RedirectView.as_view(url=settings.STATIC_URL + 'index.html'), name='index-html-redirect'),
    ]
