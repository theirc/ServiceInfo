# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations
from django.conf import settings


def remove_service_icons(apps, schema_editor):
    ServiceType = apps.get_model('services', 'ServiceType')
    service_numbers = [number for number, _ in st_icon_image_names]
    service_type = ServiceType.objects.filter(number__in=service_numbers).update(icon='')


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0031_servicetype_icon'),
    ]

    operations = [
    ]
