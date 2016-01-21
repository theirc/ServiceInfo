# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('service_info_cms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('average_rating', models.IntegerField(default=0)),
                ('num_ratings', models.IntegerField(default=0)),
                ('rating_total', models.IntegerField(default=0)),
                ('page_obj', models.ForeignKey(to='cms.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatingExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('include_rating', models.BooleanField(default=False)),
                ('extended_object', models.OneToOneField(to='cms.Page', editable=False)),
                ('public_extension', models.OneToOneField(to='service_info_cms.RatingExtension', editable=False, related_name='draft_extension', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
