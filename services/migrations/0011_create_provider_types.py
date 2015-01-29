# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


INITIAL_TYPES = [
    dict(number=1, name_en="Local NGO", name_ar="منظمة غير حكومية محلية"),
    dict(number=2, name_en="International NGO", name_ar="منظمة غير حكومية عالمية"),
    dict(number=3, name_en="Public Hospitals", name_ar="مستشفيات حكومية"),
    dict(number=4, name_en="Public Schools", name_ar="مدارس رسمية"),
    dict(number=5, name_en="Private Hospitals", name_ar="مستشفيات خاصة"),
    dict(number=6, name_en="Private Schools", name_ar="مدارس خاصة"),
    dict(number=7, name_en="Community Centers", name_ar="مراكز إجتماعية"),
    dict(number=8, name_en="UN Agency", name_ar="وكالة الأمم المتحدة"),
]


def no_op(apps, schema_editor):
    pass


def create_types(apps, schema_editor):
    ProviderType = apps.get_model('services', 'ProviderType')
    for value in INITIAL_TYPES:
        ProviderType.objects.get_or_create(
            number=value['number'],
            defaults=value,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_create_service_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='providertype',
            name='number',
            field=models.IntegerField(unique=True, default=0),
            preserve_default=False,
        ),
        migrations.RunPython(create_types, no_op),
    ]



