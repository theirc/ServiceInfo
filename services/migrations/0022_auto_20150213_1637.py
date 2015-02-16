# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0021_auto_20150212_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='superseded_draft',
            field=models.ForeignKey(to='services.Service', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft')], verbose_name='update type', max_length=22),
            preserve_default=True,
        ),
    ]
