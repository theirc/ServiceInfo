# -*- coding: utf-8 -*-
"""Create initial service types if they don't already exist,
but don't clobber their data if they do exist already.
"""

from __future__ import unicode_literals

from django.db import models, migrations


INITIAL_TYPES = [
    dict(number=1, name_en='Education Services', name_ar='خدمات التعليم'),
    dict(number=2, name_en='Health Services', name_ar='الخدمات الصحية',
         comments_en='including psychosocial and disabilities'),
    dict(number=3, name_en='Shelter & Wash Services', name_ar='المأوى وخدمات الصرف الصحي والنظافة',
         comments_en='including shelter rehabilitation'),
    dict(number=4, name_en='Financial services', name_ar='الخدمات المالية',
         comments_en='including unconditional cash assistance'),
    dict(number=5, name_en='Legal services', name_ar='الخدمات القانونية'),
    dict(number=6, name_en='Food Security', name_ar='الإعاشات الغذائية'),
    dict(number=7, name_en='Material Support (excluding cash and food)',
         name_ar='المساعدات العينية الغير غذائية والغير مالية'),
    dict(number=8, name_en='Community centers', name_ar='المراكز الإجتماعية',
         comments_en='including vocational trainings and awareness sessions'),
]


def no_op(apps, schema_editor):
    pass


def create_types(apps, schema_editor):
    ServiceType = apps.get_model('services', 'ServiceType')
    for value in INITIAL_TYPES:
        ServiceType.objects.get_or_create(
            number=value['number'],
            defaults=value,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20150127_1348'),
    ]

    operations = [
        migrations.RunPython(create_types, no_op),
    ]
