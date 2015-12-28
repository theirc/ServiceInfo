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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('icon_name', models.CharField(max_length=80, help_text='Choose an icon at http://materializecss.com/icons.html', verbose_name='Materialize icon name')),
                ('extended_object', models.OneToOneField(to='cms.Page', editable=False)),
                ('public_extension', models.OneToOneField(null=True, to='service_info_cms.IconNameExtension', editable=False, related_name='draft_extension')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
