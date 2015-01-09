# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('type', models.IntegerField(choices=[(1, 'Provider type 1'), (2, 'Provider type 2')], verbose_name='type')),
                ('phone_number', models.CharField(max_length=20, verbose_name='phone number')),
                ('email', models.EmailField(max_length=75, default='', blank=True, verbose_name='email')),
                ('website', models.URLField(default='', blank=True, verbose_name='website')),
                ('description', models.TextField(verbose_name='description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SelectionCriterion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('hours_of_service', models.TextField(verbose_name='hours of service')),
                ('additional_info', models.TextField(default='', blank=True, verbose_name='additional info')),
                ('cost_of_service', models.TextField(default='', blank=True, verbose_name='cost of service')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceArea',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='area_of_service',
            field=models.ForeignKey(to='services.ServiceArea', verbose_name='area of service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='provider',
            field=models.ForeignKey(to='services.Provider', verbose_name='provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='selection_criteria',
            field=models.ManyToManyField(to='services.SelectionCriterion', verbose_name='selection criteria'),
            preserve_default=True,
        ),
    ]
