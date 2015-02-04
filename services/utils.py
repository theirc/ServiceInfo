import logging

from django.contrib.auth.models import Permission


logger = logging.getLogger(__name__)


# Typical provider/user permissions
USER_PERMISSION_NAMES = [
    'services.add_provider', 'services.change_provider',
    'services.add_service', 'services.change_service',
    'services.add_selectioncriterion', 'services.change_selectioncriterion',
]


def permission_names_to_objects(names):
    """
    Given an iterable of permission names (e.g. 'app_label.add_model'),
    return an iterable of Permission objects for them.  The permission
    must already exist, because a permission name is not enough information
    to create a new permission.
    """
    result = []
    for name in names:
        app_label, codename = name.split(".", 1)
        # Is that enough to be unique? Hope so
        try:
            result.append(Permission.objects.get(content_type__app_label=app_label,
                                                 codename=codename))
        except Permission.DoesNotExist:
            logger.exception("NO SUCH PERMISSION: %s, %s" % (app_label, codename))
            raise
    return result
