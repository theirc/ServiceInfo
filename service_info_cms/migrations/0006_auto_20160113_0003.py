# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('service_info_cms', '0005_auto_20160112_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagerating',
            name='extended_object',
        ),
        migrations.RemoveField(
            model_name='pagerating',
            name='page_title',
        ),
        migrations.RemoveField(
            model_name='pagerating',
            name='public_extension',
        ),
        migrations.AddField(
            model_name='pagerating',
            name='page_obj',
            field=models.ForeignKey(default=1, to='cms.Page'),
            preserve_default=False,
        ),
    ]
