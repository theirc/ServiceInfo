# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0019_fix_production_site_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='update_of',
            field=models.ForeignKey(help_text='If a service record represents a modification of an existing service record that is still pending approval, this field links to the existing service record.', related_name='pending_update', blank=True, to='services.Service', null=True),
            preserve_default=True,
        ),
    ]
