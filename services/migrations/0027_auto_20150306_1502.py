# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0026_auto_20150302_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='by',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(verbose_name='update type', choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft'), ('approve-service', 'Staff approved a new or changed service'), ('rejected-service', 'Staff rejected a new or changed service')], max_length=22),
            preserve_default=True,
        ),
    ]
