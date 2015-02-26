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
            name='number_of_monthly_beneficiaries',
            field=models.IntegerField(null=True, verbose_name='number of targeted beneficiaries monthly', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000)], blank=True),
            preserve_default=True,
        ),
    ]
