# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0023_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='phone_number',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], verbose_name='phone number'),
            preserve_default=True,
        ),
    ]
