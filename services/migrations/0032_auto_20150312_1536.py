# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations
from django.conf import settings
from django.core.files import File

st_icon_image_names = (
    (1, 'education_64px.png'),
    (2, 'health_64px.png'),
    (3, 'wash_shower_64px.png'),
    (4, 'financing_64px.png'),
    (5, 'law_64px.png'),
    (6, 'food_NFI_food_64px.png'),
    (7, 'nonfood_support_item_64px.png'),
    (8, 'community_building_64px.png'),
)

EXISTING_ICON_DIRECTORY = os.path.join(settings.PROJECT_ROOT, 'frontend', 'images')


def populate_service_icons(apps, schema_editor):
    ServiceType = apps.get_model('services', 'ServiceType')
    for st_number, icon_fname in st_icon_image_names:
        icon_file = open(os.path.join(EXISTING_ICON_DIRECTORY, icon_fname), 'rb')
        service_type = ServiceType.objects.get(number=st_number)
        service_type.icon.save(icon_fname, File(icon_file))


def remove_service_icons(apps, schema_editor):
    ServiceType = apps.get_model('services', 'ServiceType')
    service_numbers = [number for number, _ in st_icon_image_names]
    service_type = ServiceType.objects.filter(number__in=service_numbers).update(icon='')


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0031_servicetype_icon'),
    ]

    operations = [
        migrations.RunPython(populate_service_icons, remove_service_icons),
    ]
