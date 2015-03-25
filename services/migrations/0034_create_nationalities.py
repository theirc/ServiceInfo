# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

INITIAL_NATIONALITIES = [
    dict(number=1, name_en='Lebanese', name_ar='لبناني'),
    dict(number=2, name_en='Lebanese returnees from Syria', name_ar='لبناني عائد من سوريا'),
    dict(number=3, name_en='Palestine refugees in Lebanon', name_ar='فلسطيني مقيم في لبنان'),
    dict(number=4, name_en='Palestine refugees from Syria', name_ar='فلسطيني عائد من سوريا'),
    dict(number=5, name_en='Syrian', name_ar='سوري'),
    dict(number=6, name_en='Iraqi', name_ar='عراقي'),
    dict(number=7, name_en='Other', name_ar='جنسيات أخرى'),
]


def no_op(apps, schema_editor):
    pass


def create_nationalities(apps, schema_editor):
    Nationality = apps.get_model('services', 'Nationality')
    for value in INITIAL_NATIONALITIES:
        Nationality.objects.get_or_create(
            number=value['number'],
            defaults=value,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0033_auto_20150316_1542'),
    ]

    operations = [
        migrations.RunPython(create_nationalities, no_op),
    ]
