# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_types(apps, schema_editor):
    # The reverse migration removes the number field, which
    # means we have no way to add it right
    ProviderType = apps.get_model('services', 'ProviderType')
    ProviderType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_providertype_number'),
    ]

    operations = [
    ]



