# -*- coding: utf-8 -*-
"""Create Groups with the permissions we want.

(This is ridiculously complicated to do in a migration.)
"""
from __future__ import unicode_literals
from django.db import models, migrations
from services.utils import permission_names_to_objects


# Permissions needed by staff
# Permission names are "applabel.action_lowercasemodelname"
STAFF_PERMISSIONS = [
    'services.change_provider',
    'services.change_service'
]

# Typical provider permissions
PROVIDER_PERMISSIONS = [
    'services.add_provider',
    'services.change_provider',
    'services.add_service',
    'services.change_service',
    'services.add_selectioncriterion',
    'services.change_selectioncriterion',
]


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Staff', 'Providers']).delete()


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    group, unused = Group.objects.get_or_create(name='Staff')
    group.permissions.add(*permission_names_to_objects(STAFF_PERMISSIONS, Permission, ContentType))

    group, unused = Group.objects.get_or_create(name='Providers')
    group.permissions.add(*permission_names_to_objects(PROVIDER_PERMISSIONS, Permission, ContentType))


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__first__'),
        ('services', '0015_merge'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
