import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


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
