# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
    ]

    operations = [
        migrations.CreateModel(
            name='IconNameExtension',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('icon_name', models.CharField(max_length=80, help_text='Please provide the name of a Materialize icon', verbose_name='Materialize icon name')),
                ('extended_object', models.OneToOneField(editable=False, to='cms.Page')),
                ('public_extension', models.OneToOneField(editable=False, null=True, to='service_info_cms.IconNameExtension', related_name='draft_extension')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
