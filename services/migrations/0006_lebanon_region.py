# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_add_top_level_service_areas'),
    ]

    operations = [
        migrations.CreateModel(
            name='LebanonRegion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'Governate'), (2, 'District or CAZA')])),
                ('area', models.FloatField()),
                ('perimeter', models.FloatField()),
                ('moh_na', models.CharField(help_text='Seems to be the governate', max_length=25)),
                ('moh_cod', models.CharField(help_text='Seems to be the governate', max_length=5)),
                ('kada_name', models.CharField(help_text='Seems to be the CAZA or district', default='', max_length=28, blank=True)),
                ('kadaa_code', models.CharField(help_text='Seems to be the CAZA or district', default='', max_length=10, blank=True)),
                ('cad_name', models.CharField(default='', max_length=60, blank=True)),
                ('cad_code', models.CharField(default='', max_length=16, blank=True)),
                ('shape_leng', models.FloatField()),
                ('shape_area', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('name', models.CharField(max_length=60)),
                ('code', models.CharField(max_length=16)),
                ('parent', models.ForeignKey(null=True, blank=True, related_name='children', to='services.LebanonRegion')),
            ],
            options={
                'ordering': ['level', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='servicearea',
            name='region',
        ),
        migrations.AddField(
            model_name='servicearea',
            name='lebanon_region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, default=None, to='services.LebanonRegion'),
            preserve_default=True,
        ),
    ]
