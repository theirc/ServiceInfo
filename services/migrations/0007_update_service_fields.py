# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_add_non_english_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='hours_of_service',
        ),
        migrations.AddField(
            model_name='provider',
            name='number_of_monthly_beneficiaries',
            field=models.IntegerField(default=0, verbose_name='number of targeted beneficiaries monthly'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='selectioncriterion',
            name='text_ar',
            field=models.CharField(default='', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selectioncriterion',
            name='text_en',
            field=models.CharField(default='', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selectioncriterion',
            name='text_fr',
            field=models.CharField(default='', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='friday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='friday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, verbose_name='location', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='monday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='monday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='saturday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='saturday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='sunday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='sunday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='thursday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='thursday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='tuesday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='tuesday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='wednesday_close',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='wednesday_open',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='servicearea',
            name='name',
            field=models.CharField(default='area', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicearea',
            name='parent',
            field=models.ForeignKey(null=True, to='services.ServiceArea', help_text='the area that contains this area', verbose_name='parent area', related_name='children', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='servicearea',
            name='region',
            field=django.contrib.gis.db.models.fields.PolygonField(null=True, srid=4326, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='selection_criteria',
            field=models.ManyToManyField(to='services.SelectionCriterion', verbose_name='selection criteria', blank=True),
            preserve_default=True,
        ),
    ]
