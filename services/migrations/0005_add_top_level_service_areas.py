# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from services.utils import update_postgres_sequence_generator


def no_op(apps, schema_editor):
    pass


def create_areas(apps, schema_editor):
    ServiceArea = apps.get_model('services', 'ServiceArea')

    ServiceArea.objects.update_or_create(
        pk=27,
        defaults=dict(
            name_en="Mount Lebanon",
            name_ar="جبل لبنان",
        )
    )
    ServiceArea.objects.update_or_create(
        pk=28,
        defaults=dict(
            name_en="Tripoli and surroundings",
            name_ar="طرابلس وضواحيها",
        )
    )

    update_postgres_sequence_generator(ServiceArea)


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_service_is_mobile'),
    ]

    operations = [
        migrations.RunPython(create_areas, no_op),
    ]
