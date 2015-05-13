# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models, migrations


def define_sites(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # These names changed after the initial migration (0008) was run,
    # so make sure they're updated now.
    Site.objects.update_or_create(
        id=settings.DEV_SITE_ID,
        defaults=dict(
            name='IRC ServiceInfo Dev',
            domain='localhost:8000',
        )
    )
    Site.objects.update_or_create(
        id=settings.STAGING_SITE_ID,
        defaults=dict(
            name='IRC ServiceInfo Staging',
            domain='serviceinfo-staging.rescue.org',
        )
    )
    Site.objects.update_or_create(
        id=settings.PRODUCTION_SITE_ID,
        defaults=dict(
            name='IRC ServiceInfo',
            domain='serviceinfo.rescue.org',
        )
    )

def no_op(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_squashed_0038_last_migration'),
    ]

    operations = [
        migrations.RunPython(define_sites, no_op),
    ]
