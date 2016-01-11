# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_info_cms', '0002_ratingextension'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratingextension',
            name='rating',
        ),
        migrations.AddField(
            model_name='ratingextension',
            name='include_rating',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
