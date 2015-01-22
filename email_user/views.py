import logging

from django.conf import settings
from django.contrib.auth import get_user_model, login, get_backends
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class ActivationView(TemplateView):
    """
    Base class for user activation views.

    """
    http_method_names = ['get']
    template_name = 'registration/activation_failed.html'

    def get(self, request, *args, **kwargs):
        activated_user = self.activate(request, *args, **kwargs)
        if activated_user:
            success_url = self.get_success_url(request, activated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return super(ActivationView, self).get(request, *args, **kwargs)

    def get_success_url(self, request, user):
        return settings.ACCOUNT_ACTIVATION_REDIRECT_URL

    def activate(self, request, activation_key):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the user will be logged
        in on the current session and the user object
        is returned.

        If not successful, returns False.
        """

        try:
            activated_user = get_user_model().objects.activate_user(activation_key)
        except ValidationError:
            logger.debug("Unable to activate user", exc_info=True)
            return False
        else:
            # Log the user in - copied from django-registration too
            backend = get_backends()[0]  # Hack to bypass `authenticate()`.
            activated_user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            request.user = activated_user
            login(request, activated_user)
            request.session.modified = True
            return activated_user
