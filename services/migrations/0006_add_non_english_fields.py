# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_rename_english_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='description_ar',
            field=models.TextField(default='', verbose_name='description in Arabic', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='description_fr',
            field=models.TextField(default='', verbose_name='description in French', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='name_ar',
            field=models.CharField(default='', max_length=256, verbose_name='name in Arabic', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='name_fr',
            field=models.CharField(default='', max_length=256, verbose_name='name in French', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='additional_info_ar',
            field=models.TextField(default='', verbose_name='additional information in Arabic', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='additional_info_fr',
            field=models.TextField(default='', verbose_name='additional information in French', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='description_ar',
            field=models.TextField(default='', verbose_name='description in Arabic', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='description_fr',
            field=models.TextField(default='', verbose_name='description in French', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='name_ar',
            field=models.CharField(default='', max_length=256, verbose_name='name in Arabic', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='name_fr',
            field=models.CharField(default='', max_length=256, verbose_name='name in French', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='description_en',
            field=models.TextField(default='', verbose_name='description in English', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_en',
            field=models.CharField(default='', max_length=256, verbose_name='name in English', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='additional_info_en',
            field=models.TextField(default='', verbose_name='additional information in English', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='description_en',
            field=models.TextField(verbose_name='description in English'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='name_en',
            field=models.CharField(default='', max_length=256, verbose_name='name in English', blank=True),
            preserve_default=True,
        ),
    ]
