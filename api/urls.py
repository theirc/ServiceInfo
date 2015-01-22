from django.conf.urls import url, include
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
# base_name: override URL names for our user model - default would
# be based on 'email_user' but we want to base them on 'user' instead.
router.register(r'users', views.UserViewSet, base_name='user')
router.register(r'groups', views.GroupViewSet)
router.register(r'providers', views.ProviderViewSet)
router.register(r'providertypes', views.ProviderTypeViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'serviceareas', views.ServiceAreaViewSet)

# See http://www.django-rest-framework.org/api-guide/routers/ for the
# URL names that DRF comes up with, to make it easy to reverse them.

urlpatterns = [
    # Wire up our API using automatic URL routing.
    url(r'^', include(router.urls)),

    # Provide a special call to get an auth token
    # (This will end up as something like "/api/login/")
    url(r'^login/$', views.APILogin.as_view(), name='api-login'),

    # Activate a user
    url(r'^activate/$', view=views.APIActivationView.as_view(), name='api-activate'),

    # Additionally, we include login URLs for the browsable API.
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
