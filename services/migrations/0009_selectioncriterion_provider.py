# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_add_sites'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectioncriterion',
            name='provider',
            field=models.ForeignKey(default=0, to='services.Provider'),
            preserve_default=False,
        ),
    ]
