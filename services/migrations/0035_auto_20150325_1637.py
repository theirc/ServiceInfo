# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0034_create_nationalities'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nationality',
            options={'verbose_name_plural': 'nationalities'},
        ),
        migrations.AlterField(
            model_name='feedback',
            name='difficulty_contacting',
            field=models.CharField(choices=[('no', 'No'), ('didntknow', 'Did not know how to contact them'), ('nophoneresponse', 'Tried to contact them by phone but received no response'), ('noresponse', 'Tried to contact them in person but received no response or did not find their office'), ('unhelpful', 'Contacted them but response was unhelpful'), ('other', 'Other')], max_length=20, help_text='Did you experience difficulties contacting the provider of the service you needed?'),
            preserve_default=True,
        ),
    ]
