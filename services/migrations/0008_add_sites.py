# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
from services.utils import update_postgres_sequence_generator


def no_op(apps, schema_editor):
    pass


def define_sites(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=settings.DEV_SITE_ID,
        defaults=dict(
            name='IRC Service Info Dev',
            domain='localhost:8000',
        )
    )
    Site.objects.update_or_create(
        id=settings.STAGING_SITE_ID,
        defaults=dict(
            name='IRC Service Info Staging',
            domain='serviceinfo-staging.rescue.org',
        )
    )
    Site.objects.update_or_create(
        id=settings.PRODUCTION_SITE_ID,
        defaults=dict(
            name='IRC Service Info',
            domain='serviceinfo-staging.rescue.org',
        )
    )
    update_postgres_sequence_generator(Site, 'default')


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_update_service_fields'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(define_sites, no_op),
    ]
