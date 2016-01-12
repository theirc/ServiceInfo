# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('service_info_cms', '0004_pagerating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagerating',
            name='page_id',
        ),
        migrations.AddField(
            model_name='pagerating',
            name='page_title',
            field=models.ForeignKey(default=1, to='cms.Title'),
            preserve_default=False,
        ),
    ]
