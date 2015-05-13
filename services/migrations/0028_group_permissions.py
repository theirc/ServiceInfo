# -*- coding: utf-8 -*-
# There was a bug in how we added group permissions in an earlier migration
from __future__ import unicode_literals

from django.db import models, migrations


def no_op(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0027_auto_20150310_1501'),
    ]

    operations = [
    ]
