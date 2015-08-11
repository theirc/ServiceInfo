# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_auto_20150727_2318'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicetype',
            options={'ordering': ['number']},
        ),
    ]
