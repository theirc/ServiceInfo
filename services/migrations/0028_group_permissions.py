# -*- coding: utf-8 -*-
# There was a bug in how we added group permissions in an earlier migration
from __future__ import unicode_literals

from django.db import models, migrations


# Permissions needed by staff
# Permission names are "applabel.action_lowercasemodelname"
from services.utils import permission_names_to_objects


STAFF_PERMISSIONS = [
    'services.change_provider',
    'services.change_service',
    'services.change_selectioncriterion',
]


def add_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    group= Group.objects.get(name='Staff')
    group.permissions.add(*permission_names_to_objects(STAFF_PERMISSIONS, Permission, ContentType))


def no_op(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0027_auto_20150310_1501'),
    ]

    operations = [
        migrations.RunPython(add_permissions, no_op),
    ]
