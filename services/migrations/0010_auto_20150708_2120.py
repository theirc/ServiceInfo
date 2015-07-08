# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20150702_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='request_for_service',
            field=models.ForeignKey(null=True, related_name='jira_records', blank=True, to='services.RequestForService'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(verbose_name='update type', max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft'), ('approve-service', 'Staff approved a new or changed service'), ('rejected-service', 'Staff rejected a new or changed service'), ('feedback', 'User submitted feedback'), ('request-for-service', 'User submitted request for service.')]),
            preserve_default=True,
        ),
    ]
