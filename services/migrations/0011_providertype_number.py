# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_create_service_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='providertype',
            name='number',
            field=models.IntegerField(unique=True, default=0),
            preserve_default=False,
        ),
    ]



