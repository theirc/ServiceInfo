# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0015_merge'),
    ]

    operations = [
        # Add nullable FK
        migrations.AddField(
            model_name='selectioncriterion',
            name='service',
            field=models.ForeignKey(null=True, related_name='selection_criteria', to='services.Service'),
            preserve_default=True,
        ),
        # # Populate FK
        # migrations.RunPython(relink_criteria, backlink_criteria),
        # Remove manytomany
        migrations.RemoveField(
            model_name='service',
            name='selection_criteria',
        ),
        # Make NK not nullable
        migrations.AlterField(
            model_name='selectioncriterion',
            name='service',
            field=models.ForeignKey(related_name='selection_criteria', to='services.Service'),
            preserve_default=True,
        ),
    ]
