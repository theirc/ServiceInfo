import os
import re

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

import api.urls
from services.views import export_view, health_view, logout_view


FRONTEND_DIR = os.path.join(settings.PROJECT_ROOT, 'frontend')

# Our middleware will bypass locale middleware redirect processing
# of 404s for requests matching these patterns.  Because the Django
# CMS pattern matches anything, locale middleware thinks that
# redirecting to /<language>/api/bad might work, and the API client
# gets a hopeless 302.
NO_404_LOCALE_REDIRECTS = (re.compile(r'^/api/'),)

# Reminder: the `static` function is a no-op if DEBUG is False, as in production.
urlpatterns = [
    url(r'^health/$', health_view),
    url(r'^api/', include(api.urls)),
    url(r'^', include('service_info_cms.urls')),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
    url(r'^export/(?P<signature>.*)/$', export_view, name='export'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^captcha/', include('captcha.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += i18n_patterns(
    '',
    # Django admin
    url(r'^admin/', include(admin.site.urls)),
    # Django CMS
    url(r'^', include('cms.urls', app_name=settings.CMS_APP_NAME)),
)
