# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_user', '0003_emailuser_activation_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailuser',
            name='language',
            field=models.CharField(help_text="User's preferred language.", max_length=10, blank=True, default='', verbose_name='language'),
            preserve_default=True,
        ),
    ]
