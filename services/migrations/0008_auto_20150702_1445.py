# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_load_geo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='staff_satisfaction',
            field=models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], help_text='How would you rate your satisfaction with the staff of the organization that provided services to you, (from 1 to 5, where 5 is the highest rating possible)?', blank=True, null=True, default=None),
            preserve_default=True,
        ),
    ]
