# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


def no_op(apps, schema_editor):
    pass


def define_sites(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=settings.DEV_SITE_ID,
        defaults=dict(
            name='Bob Dev',
            domain='bob-dev.caktusgroup.com',
        )
    )
    Site.objects.update_or_create(
        id=settings.STAGING_SITE_ID,
        defaults=dict(
            name='Bob Staging',
            domain='bob-staging.caktusgroup.com',
        )
    )
    Site.objects.update_or_create(
        id=settings.PRODUCTION_SITE_ID,
        defaults=dict(
            name='Bob',
            domain='bob.caktusgroup.com',
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_update_service_fields'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(define_sites, no_op),
    ]
