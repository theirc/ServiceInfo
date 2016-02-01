import logging

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connections
from django.db.models import Max
from django.forms.utils import ErrorDict, ErrorList


logger = logging.getLogger(__name__)


def permission_names_to_objects(names, permission_model=None, contenttype_model=None):
    """
    Given an iterable of permission names (e.g. 'app_label.add_model'),
    return an iterable of Permission objects for them.
    """
    if not permission_model:
        permission_model = Permission
    if not contenttype_model:
        contenttype_model = ContentType
    result = []
    for name in names:
        app_label, codename = name.split(".", 1)
        # Is that enough to be unique? Hope so
        try:
            result.append(permission_model.objects.get(content_type__app_label=app_label,
                                                       codename=codename))
        except permission_model.DoesNotExist:
            action, lowercasemodelname = codename.split('_', 1)
            content_type, created = contenttype_model.objects.get_or_create(
                app_label=app_label,
                model=lowercasemodelname,
                )
            result.append(permission_model.objects.create(
                name=codename,
                codename=codename,
                content_type=content_type,
                ))
    return result


def validation_error_as_text(error):
    """
    Given a ValidationError object, return a string representing the errors.
    """
    try:
        ed = ErrorDict(error.message_dict)
        return ed.as_text()
    except AttributeError:
        el = ErrorList(error.messages)
        return el.as_text()


def absolute_url(path):
    """
    Given the path part of a URL in our site,
    prefix it with the appropriate scheme, domain, and optionally
    port, and return the complete result.
    """

    site = Site.objects.get_current()
    scheme = 'https' if settings.SECURE_LINKS else 'http'
    return '%s://%s%s' % (scheme, site.domain, path)


def get_path_to_service(service_id):
    """In lieu of a url-reversing mechanism for routes in the app"""
    return '/app/index.html#/service/%d' % service_id


def update_postgres_sequence_generator(model, db='default'):
    """
    Update the sequence generator for a model's primary key
    to the max current value of that key, so that Postgres
    will know not to try to use the previously-used values again.

    Apparently this is needed because when we create objects
    during the migration, we specify the primary key's value,
    so the Postgres sequence doesn't get used or incremented.

    :param db: Key for the database setting for the database to use
    """
    # This is specific to Postgres
    if 'backends.post' not in settings.DATABASES[db]['ENGINE']:
        return
    table_name = model._meta.db_table
    attname, colname = model._meta.pk.get_attname_column()
    seq_name = "%s_%s_seq" % (table_name, colname)
    max_val = model.objects.aggregate(maxkey=Max(attname))['maxkey']
    cursor = connections[db].cursor()
    cursor.execute("select setval(%s, %s);", [seq_name, max_val])
