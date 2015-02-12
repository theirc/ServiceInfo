# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0020_auto_20150209_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='done',
            field=models.BooleanField(verbose_name="Whether this record's work has been done", default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='locked',
            field=models.BooleanField(verbose_name='Whether a task is currently updating this record', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service')], verbose_name='update type', max_length=22),
            preserve_default=True,
        ),
    ]
