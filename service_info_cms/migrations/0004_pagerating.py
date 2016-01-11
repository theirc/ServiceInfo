# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('service_info_cms', '0003_auto_20160111_1846'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageRating',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('average_rating', models.DecimalField(default=False, decimal_places=2, max_digits=3)),
                ('num_ratings', models.IntegerField()),
                ('rating_total', models.IntegerField()),
                ('page_id', models.IntegerField()),
                ('extended_object', models.OneToOneField(editable=False, to='cms.Page')),
                ('public_extension', models.OneToOneField(editable=False, null=True, related_name='draft_extension', to='service_info_cms.PageRating')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
