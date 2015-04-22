"""
Copied and adapted from
https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#a-full-example
"""
import re

import hashlib
import random

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, activate, get_language

from rest_framework.authtoken.models import Token
import six


SHA1_RE = re.compile('^[a-f0-9]{40}$')
PASSWORD_RESET_KEY_RE = re.compile(
    r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$')
token_generator = PasswordResetTokenGenerator()


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

        If the key is valid, return the ``User`` after activating.

        Raises django's ValidationError exception:

        * If the key is not valid

        * If the key is valid but the ``User`` is already active

        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``RegistrationProfile.ACTIVATED``
        after successful activation.

        """
        try:
            user = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            msg = _('Activation key is invalid or has already been used.')
            raise ValidationError(msg)
        user.is_active = True
        user.activation_key = self.model.ACTIVATED
        user.save()
        return user

    def validate_password_reset_key(self, key):
        """
        Given a key that came from get_password_reset_key, and
        is still valid (they expire, or become invalid if the user's password
        or last login time changes), return the user object that
        the key is for.  Else, return None.
        :param key: A key that came from get_password_key (presumably)
        :return: an EmailUser object, or None.
        """
        m = PASSWORD_RESET_KEY_RE.match(key)
        if not m:
            return None
        uidb64 = m.group('uidb64')
        token = m.group('token')
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = self.get(pk=uid)
        except (TypeError, ValueError, OverflowError, self.model.DoesNotExist):
            user = None
        else:
            if token_generator.check_token(user, token):
                return user
        return None

    def get_by_natural_key(self, username):
        return self.get(**{"%s__iexact" % self.model.USERNAME_FIELD: username})


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

    language = models.CharField(
        _('language'),
        help_text=_('User\'s preferred language.'),
        max_length=10,
        default='',
        blank=True,
    )

    objects = EmailUserManager()

    class Meta(object):
        verbose_name = _("user")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Enforce unique email address, case-insensitive
    def save(self, *args, **kwargs):
        others = type(self).objects.filter(email__iexact=self.email)
        if self.pk:
            others = others.exclude(pk=self.pk)
        if others.exists():
            raise ValidationError(_("User emails must be unique without regard to case."))
        super().save(*args, **kwargs)

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

    def create_activation_key(self):
        salt = hashlib.sha1(six.text_type(random.random()).encode('ascii')).hexdigest()[:5]
        salt = salt.encode('ascii')
        email = self.email
        if isinstance(email, six.text_type):
            username = email.encode('utf-8')
        return hashlib.sha1(salt+username).hexdigest()

    def has_valid_activation_key(self):
        return not self.is_active and self.activation_key and self.activation_key != self.ACTIVATED

    def set_password(self, raw_password):
        min_length = getattr(settings, 'MINIMUM_PASSWORD_LENGTH', None)
        if min_length and len(raw_password) < min_length:
            msg = _("Password is too short. It must have at least {min_length} characters.")
            raise ValidationError(msg.format(min_length=min_length))
        super().set_password(raw_password)

    def send_activation_email(self, site, request, base_activation_link):
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
            'activation_link': base_activation_link + self.activation_key,
            'site': site,
        })
        self.send_email_to_user(ctx_dict,
                                'registration/activation_email_subject.txt',
                                'registration/activation_email.txt',
                                'registration/activation_email.html'
                                )
        self.save()

    def get_activation_link(self, base_activation_link):
        """
        Appends the activation key to the base_activation_link and
        returns it.
        :param base_activation_link:
        :return:
        """
        return base_activation_link + self.activation_key

    def get_password_reset_key(self):
        """
        Return a long opaque string that can be re-used in other methods
        to allow changing the user's password without knowing the current one.
        This uses Django's default mechanisms.
        :return: A long string
        """
        uidb64 = urlsafe_base64_encode(force_bytes(self.pk))
        token = token_generator.make_token(self)
        key = "%s/%s" % (uidb64.decode('utf-8'), token)
        return key

    def send_password_reset_email(self, base_url, site):
        ctx_dict = {
            'user': self,
            'reset_link': base_url + self.get_password_reset_key(),
            'site': site,
        }
        self.send_email_to_user(
            ctx_dict,
            'registration/password_reset_subject.txt',
            'email_user/password_reset_email.txt',
            'email_user/password_reset_email.html',
        )

    def send_email_to_user(self, ctx_dict, subject_template, message_text_template,
                           message_html_template):
        """Construct an email from a context and templates and send it to the
        user, translating if we know their preferred language.
        """
        cur_language = get_language()
        try:
            if self.language:
                # We know the user's preferred language, so use it:
                activate(self.language)

            subject = render_to_string(subject_template, ctx_dict)
            # Email subject *must not* contain newlines
            subject = (' '.join(subject.splitlines())).strip()

            message_txt = render_to_string(message_text_template, ctx_dict)
            try:
                message_html = render_to_string(message_html_template, ctx_dict)
            except TemplateDoesNotExist:
                message_html = None

            send_mail(
                subject=subject,
                message=message_txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
                html_message=message_html
            )
        finally:
            # Put language back to what it was
            activate(cur_language)


# Create an auth token for each user when they're created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
