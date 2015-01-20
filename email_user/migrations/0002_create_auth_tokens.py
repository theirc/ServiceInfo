# -*- coding: utf-8 -*-
"""Create auth tokens for existing users"""
from __future__ import unicode_literals

from django.db import models, migrations


def no_op(apps, schema_editor):
    pass


def create_auth_tokens(apps, schema_editor):
    User = apps.get_model('email_user', 'EmailUser')
    Token = apps.get_model('authtoken', 'Token')

    for user in User.objects.all():
        Token.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('email_user', '0001_initial'),
        ('authtoken', '0001_initial')
    ]

    operations = [
        migrations.RunPython(
            code=create_auth_tokens,
            reverse_code=no_op,
        )
    ]
