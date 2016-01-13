# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_info_cms', '0007_auto_20160113_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagerating',
            name='average_rating',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
