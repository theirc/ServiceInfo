# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='selectioncriterion',
            options={'verbose_name_plural': 'selection criteria'},
        ),
        migrations.RemoveField(
            model_name='provider',
            name='email',
        ),
        # Default to user #1. That user might not exist, but we have to have
        # some default to add a non-nullable field, and there probably won't be
        # any existing providers when we run this migration anyway.
        migrations.AddField(
            model_name='provider',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, default=1, help_text='user account for this provider', verbose_name='user'),
            preserve_default=False,
        ),
    ]
