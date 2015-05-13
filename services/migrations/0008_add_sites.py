# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
from services.utils import update_postgres_sequence_generator




class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_update_service_fields'),
        ('sites', '0001_initial'),
    ]

    operations = [
    ]
