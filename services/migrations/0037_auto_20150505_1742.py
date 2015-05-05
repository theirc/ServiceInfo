# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0036_auto_20150327_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='area_of_residence',
            field=models.ForeignKey(to='services.ServiceArea', verbose_name='Area of residence'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='delivered',
            field=models.BooleanField(help_text='Was service delivered?', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='name',
            field=models.CharField(max_length=256, verbose_name='Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='nationality',
            field=models.ForeignKey(to='services.Nationality', verbose_name='Nationality'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='phone_number',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], verbose_name='Phone Number (NN-NNNNNN)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='service',
            field=models.ForeignKey(to='services.Service', verbose_name='Service'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='wait_time',
            field=models.CharField(help_text='How long did you wait for the service to be delivered, after contacting the service provider?', choices=[('lesshour', 'Less than 1 hour'), ('uptotwodays', 'Up to 2 days'), ('3-7days', '3-7 days'), ('1-2weeks', '1-2 weeks'), ('more', 'More than 2 weeks')], default=None, max_length=12, null=True, blank=True),
            preserve_default=True,
        ),
    ]
