# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import services.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_auto_20150702_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestForService',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('provider_name', models.CharField(validators=[services.models.at_least_one_letter], max_length=256)),
                ('service_name', models.CharField(validators=[services.models.at_least_one_letter], max_length=256)),
                ('address', models.TextField()),
                ('contact', models.TextField()),
                ('description', models.TextField()),
                ('rating', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], help_text='How would you rate the quality of the service you received (from 1 to 5, where 5 is the highest rating possible)?')),
                ('area_of_service', models.ForeignKey(to='services.ServiceArea', verbose_name='area of service')),
                ('service_type', models.ForeignKey(to='services.ServiceType', verbose_name='type')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
