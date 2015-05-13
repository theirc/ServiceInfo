# -*- coding: utf-8 -*-
"""Create initial service types if they don't already exist,
but don't clobber their data if they do exist already.
"""

from __future__ import unicode_literals

from django.db import models, migrations



def no_op(apps, schema_editor):
    pass




class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20150127_1348'),
    ]

    operations = [
    ]
