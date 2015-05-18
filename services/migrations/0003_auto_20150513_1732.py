# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_change_name_to_serviceinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='user',
            field=models.OneToOneField(help_text='user account for this provider', verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='providertype',
            name='number',
            field=models.IntegerField(unique=True),
            preserve_default=True,
        ),
    ]
