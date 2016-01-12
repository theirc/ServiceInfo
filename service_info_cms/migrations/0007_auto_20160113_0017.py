# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_info_cms', '0006_auto_20160113_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagerating',
            name='num_ratings',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pagerating',
            name='rating_total',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
