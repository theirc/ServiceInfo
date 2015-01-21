from django.conf.urls import url
from email_user.views import ActivationView


urlpatterns = [
    url(r'^activate/(?P<activation_key>.*)/$',
        view=ActivationView.as_view(),
        name='registration_activate'),
]
