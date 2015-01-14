# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20150112_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name_en', models.CharField(blank=True, verbose_name='name in English', max_length=256, default='')),
                ('name_fr', models.CharField(blank=True, verbose_name='name in French', max_length=256, default='')),
                ('name_ar', models.CharField(blank=True, verbose_name='name in Arabic', max_length=256, default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='provider',
            name='type',
            field=models.ForeignKey(verbose_name='type', to='services.ProviderType'),
            preserve_default=True,
        ),
    ]
