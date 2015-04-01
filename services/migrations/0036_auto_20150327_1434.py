# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0035_auto_20150325_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='feedback',
            field=models.ForeignKey(to='services.Feedback', null=True, related_name='jira_records', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft'), ('approve-service', 'Staff approved a new or changed service'), ('rejected-service', 'Staff rejected a new or changed service'), ('feedback', 'User submitted feedback')], verbose_name='update type'),
            preserve_default=True,
        ),
    ]
