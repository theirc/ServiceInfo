# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='selection_criteria',
            field=models.ManyToManyField(blank=True, to='services.SelectionCriterion', verbose_name='selection criteria', related_name='services'),
            preserve_default=True,
        ),
    ]
