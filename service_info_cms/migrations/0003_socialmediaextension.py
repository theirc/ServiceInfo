# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('service_info_cms', '0002_pagerating_ratingextension'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMediaExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('include_social_media', models.BooleanField(default=False)),
                ('extended_object', models.OneToOneField(editable=False, to='cms.Page')),
                ('public_extension', models.OneToOneField(null=True, editable=False, to='service_info_cms.SocialMediaExtension', related_name='draft_extension')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
