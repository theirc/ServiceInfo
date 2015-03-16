# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0030_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='icon',
            field=models.ImageField(upload_to='service-type-icons', blank=True, verbose_name='icon'),
            preserve_default=True,
        ),
    ]
