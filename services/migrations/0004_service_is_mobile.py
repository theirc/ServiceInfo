# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20150513_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_mobile',
            field=models.BooleanField(verbose_name='mobile service', default=False),
            preserve_default=True,
        ),
    ]
