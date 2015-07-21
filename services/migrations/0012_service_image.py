# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20150714_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='image',
            field=sorl.thumbnail.fields.ImageField(upload_to='service-images/', help_text='Supported file types include GIF, JPEG, PNG, WebP. SVG files are not supported.', default='', blank=True),
            preserve_default=True,
        ),
    ]
