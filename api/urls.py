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
router.register(r'servicetypes', views.ServiceTypeViewSet)
router.register(r'serviceareas', views.ServiceAreaViewSet)
router.register(r'selectioncriteria', views.SelectionCriterionViewSet,
                base_name='selectioncriterion')
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'nationality', views.NationalityViewSet)

# See http://www.django-rest-framework.org/api-guide/routers/ for the
# URL names that DRF comes up with, to make it easy to reverse them.

urlpatterns = [
    # Wire up our API using automatic URL routing.
    url(r'^', include(router.urls)),

    # Provide a special call to get an auth token
    # (This will end up as something like "/api/login/")
    url(r'^login/$', views.APILogin.as_view(), name='api-login'),

    # Special call to get/set current user's language
    url(r'^language/$', views.LanguageView.as_view(), name='user-language'),

    # Activate a user
    url(r'^activate/$', view=views.APIActivationView.as_view(), name='api-activate'),

    # Resend activation link
    url(r'^resend_activation_link/$', view=views.ResendActivationLinkView.as_view(),
        name='resend-activation-link'),

    # Request a password reset
    url(r'^password_reset_request/$', view=views.PasswordResetRequest.as_view(),
        name='password-reset-request'),
    # See if a password reset token appears to be valid
    url(r'^password_reset_check/$', view=views.PasswordResetCheck.as_view(),
        name='password-reset-check'),
    url(r'^password_reset/$', view=views.PasswordReset.as_view(),
        name='password-reset'),

    # Additionally, we include login URLs for the browsable API.
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
