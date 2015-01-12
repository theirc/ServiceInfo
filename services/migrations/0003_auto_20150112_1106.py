# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_auto_20150112_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='status',
            field=models.CharField(default='draft', max_length=10, choices=[('draft', 'draft'), ('current', 'current'), ('rejected', 'rejected'), ('canceled', 'canceled')], verbose_name='status'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='update_of',
            field=models.ForeignKey(related_name='pending_update', null=True, blank=True, to='services.Service', help_text='If a service record represents a modification of an existing service record that is still pending approval, this field links to the existing service record.'),
            preserve_default=True,
        ),
    ]
