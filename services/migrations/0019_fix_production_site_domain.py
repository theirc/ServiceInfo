# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


def no_op(apps, schema_editor):
    pass



class Migration(migrations.Migration):

    dependencies = [
        ('services', '0018_merge'),
    ]

    operations = [
    ]
