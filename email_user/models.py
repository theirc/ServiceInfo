"""
Copied and adapted from
https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#a-full-example
"""
import datetime
import hashlib
import random
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
import re
import six

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class EmailUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email and password.
        """
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True
        return self.create_user(email, password, **kwargs)

    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.

        If the key is valid and has not expired, return the ``User``
        after activating.

        If the key is not valid or has expired, return ``False``.

        If the key is valid but the ``User`` is already active,
        return ``False``.

        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``RegistrationProfile.ACTIVATED``
        after successful activation.

        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.is_active = True
                user.activation_key = self.model.ACTIVATED
                user.save()
                return user
        return False


class EmailUser(AbstractBaseUser, PermissionsMixin):
    ACTIVATED = "ALREADY_ACTIVATED"

    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True,
    )
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=now)

    activation_key = models.CharField(_('activation key'), max_length=40, default='')

    objects = EmailUserManager()

    class Meta(object):
        verbose_name = _("user")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_api_url(self):
        return reverse('user-detail', args=[self.id])

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    # From django-registration-redux:
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.

        Key expiration is determined by a two-step process:

        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.

        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return (self.activation_key == self.ACTIVATED or
                (self.date_joined + expiration_date <= now()))
    activation_key_expired.boolean = True

    def create_activation_key(self):
        salt = hashlib.sha1(six.text_type(random.random()).encode('ascii')).hexdigest()[:5]
        salt = salt.encode('ascii')
        email = self.email
        if isinstance(email, six.text_type):
            username = email.encode('utf-8')
        return hashlib.sha1(salt+username).hexdigest()

    def send_activation_email(self, site, request=None):
        """
        Send an activation email to the user.

        The activation email will make use of two templates:

        ``registration/activation_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``registration/activation_email.txt``
            This template will be used for the text body of the email.

        ``registration/activation_email.html``
            This template will be used for the html body of the email.

        These templates will each receive the following context
        variables:

        ``user``
            The new user account

        ``activation_key``
            The activation key for the new account.

        ``expiration_days``
            The number of days remaining during which the account may
            be activated.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.models.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        ``request``
            Optional Django's ``HttpRequest`` object from view.
            If supplied will be passed to the template for better
            flexibility via ``RequestContext``.
        """
        ctx_dict = {}
        if request is not None:
            ctx_dict = RequestContext(request, ctx_dict)
        # update ctx_dict after RequestContext is created
        # because template context processors
        # can overwrite some of the values like user
        # if django.contrib.auth.context_processors.auth is used
        self.activation_key = self.create_activation_key()
        ctx_dict.update({
            'user': self,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
        })
        subject = (getattr(settings, 'REGISTRATION_EMAIL_SUBJECT_PREFIX', '') +
                   render_to_string('registration/activation_email_subject.txt', ctx_dict))
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message_txt = render_to_string('registration/activation_email.txt', ctx_dict)
        email_message = EmailMultiAlternatives(subject, message_txt, settings.DEFAULT_FROM_EMAIL,
                                               [self.email])

        try:
            message_html = render_to_string('registration/activation_email.html', ctx_dict)
        except TemplateDoesNotExist:
            message_html = None

        if message_html:
            email_message.attach_alternative(message_html, 'text/html')

        email_message.send()
        self.save()

    def get_activation_link(self):
        """
        Return the site-independent part of the activation link - just
        the URL path, without the schema or domain.
        """
        return reverse('registration_activate',
                       kwargs=dict(activation_key=self.activation_key))
