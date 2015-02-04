# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_add_sites'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
                ('name_en', models.CharField(default='', verbose_name='name in English', blank=True, max_length=256)),
                ('name_ar', models.CharField(default='', verbose_name='name in Arabic', blank=True, max_length=256)),
                ('name_fr', models.CharField(default='', verbose_name='name in French', blank=True, max_length=256)),
                ('comments_en', models.CharField(default='', verbose_name='comments in English', blank=True, max_length=512)),
                ('comments_ar', models.CharField(default='', verbose_name='comments in Arabic', blank=True, max_length=512)),
                ('comments_fr', models.CharField(default='', verbose_name='comments in French', blank=True, max_length=512)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='type',
            field=models.ForeignKey(default=0, verbose_name='type', to='services.ServiceType'),
            preserve_default=False,
        ),
    ]
