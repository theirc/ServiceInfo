Email User for Django
=====================

(THE GOAL is to move this to a separate, pluggable app.)

This Django app is a reusable, custom user model for
Django that uses the email field in place of the username
field as the primary user identifier.

It can be used as-is or subclassed.

It supports Django permissions like the default user model.

It does not include any fields to store a user's name.
Use subclassing to do that in the best way for your app
if you need names, since there's no single best way to
represent people's names.

It's worthwhile reviewing the
`Django docs <https://docs.djangoproject.com/en/1.7/topics/auth/customizing/>`_
even when using this app. It tries to handle things for you,
but switching user models in Django will always be tricky.

Requirements
------------

* Django 1.7+
* Python 2.7 or 3.4+

Installation
------------

(Once this is a separate app, install it using pip.)

In settings, add ``'email_user'`` to ``INSTALLED_APPS`` at the front -
it must come before the default Django auth app so its templates can
override those for the default User::

    INSTALLED_APPS = (
        'email_user',
        ...,
    )

Also in settings, set the ``AUTH_USER_MODEL`` to the `app_name.model`::

    AUTH_USER_MODEL = 'email_user.EmailUser'

If you need to subclass this, then change AUTH_USER_MODEL to
point at your own class.

Then create the model::

    python manage.py migrate

After doing that, it's best to drop your database and recreate it,
because existing tables will have foreign keys to the previous
user model and trying to migrate it will be very difficult.

As a corollary, if you need to use this custom model, set it up early
in your project's development, before you have any data worth saving.

If you want to use password reset, you might add these URLs to your
URL conf somewhere::

    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),

and set LOGIN_URL in your settings if you don't have one already::

    LOGIN_URL = 'admin:login'
