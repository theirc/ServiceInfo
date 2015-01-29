# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_create_service_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='status',
            field=models.CharField(max_length=10, choices=[('draft', 'draft'), ('current', 'current'), ('rejected', 'rejected'), ('canceled', 'canceled'), ('archived', 'archived')], default='draft', verbose_name='status'),
            preserve_default=True,
        ),
    ]
