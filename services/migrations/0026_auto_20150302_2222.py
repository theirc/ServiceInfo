# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import services.models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0025_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='name_ar',
            field=models.CharField(default='', validators=[services.models.blank_or_at_least_one_letter], max_length=256, blank=True, verbose_name='name in Arabic'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_en',
            field=models.CharField(default='', validators=[services.models.blank_or_at_least_one_letter], max_length=256, blank=True, verbose_name='name in English'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_fr',
            field=models.CharField(default='', validators=[services.models.blank_or_at_least_one_letter], max_length=256, blank=True, verbose_name='name in French'),
            preserve_default=True,
        ),
    ]
