# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import services.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0026_auto_20150302_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='address_ar',
            field=models.TextField(default='', verbose_name='provider address in Arabic', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='address_en',
            field=models.TextField(default='', verbose_name='provider address in English', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='address_fr',
            field=models.TextField(default='', verbose_name='provider address in French', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_name_ar',
            field=models.CharField(default='', verbose_name='focal point name in Arabic', validators=[services.models.blank_or_at_least_one_letter], blank=True, max_length=256),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_name_en',
            field=models.CharField(default='', verbose_name='focal point name in English', validators=[services.models.blank_or_at_least_one_letter], blank=True, max_length=256),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_name_fr',
            field=models.CharField(default='', verbose_name='focal point name in French', validators=[services.models.blank_or_at_least_one_letter], blank=True, max_length=256),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_phone_number',
            field=models.CharField(default='', verbose_name='focal point phone number', validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], max_length=20),
            preserve_default=False,
        ),
    ]
