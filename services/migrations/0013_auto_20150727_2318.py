# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0012_service_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='image',
            field=sorl.thumbnail.fields.ImageField(blank=True, help_text='Upload an image file (GIF, JPEG, PNG, WebP) with a square aspect ratio (Width equal to Height). The image size should be at least 1280 x 1280 for best results. SVG files are not supported.', default='', upload_to='service-images/'),
            preserve_default=True,
        ),
    ]
