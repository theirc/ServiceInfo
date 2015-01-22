# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_user', '0002_create_auth_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailuser',
            name='activation_key',
            field=models.CharField(verbose_name='activation key', default='', max_length=40),
            preserve_default=True,
        ),
    ]
