# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0028_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='update_of',
            field=models.ForeignKey(related_name='updates', blank=True, to='services.Service', null=True, help_text='If a service record represents a modification of another service record, this field links to that other record.'),
            preserve_default=True,
        ),
    ]
