# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_auto_20150708_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestforservice',
            name='rating',
            field=models.SmallIntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], default=None, help_text='How would you rate the quality of the service you received (from 1 to 5, where 5 is the highest rating possible)?', null=True),
            preserve_default=True,
        ),
    ]
