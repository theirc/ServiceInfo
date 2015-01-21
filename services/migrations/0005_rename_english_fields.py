# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_auto_20150112_1109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='provider',
            old_name='description',
            new_name='description_en',
        ),
        migrations.RenameField(
            model_name='provider',
            old_name='name',
            new_name='name_en',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='additional_info',
            new_name='additional_info_en',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='description',
            new_name='description_en',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='name',
            new_name='name_en',
        ),
    ]
