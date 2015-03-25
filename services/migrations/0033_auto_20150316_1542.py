# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import services.models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0032_auto_20150312_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('phone_number', models.CharField(max_length=20, verbose_name='phone number', validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')])),
                ('delivered', models.BooleanField(help_text='Was the service you sought delivered to you?', default=False)),
                ('quality', models.SmallIntegerField(help_text='How would you rate the quality of the service you received (from 1 to 5, where 5 is the highest rating possible)?', null=True, blank=True, default=None, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('non_delivery_explained', models.CharField(choices=[('no', 'No explanation'), ('unclear', 'Explanation was not clear'), ('unfair', 'Explanation was not fair'), ('yes', 'Clear and appropriate explanation')], help_text='Did you receive a clear explanation for why the service you sought was not delivered to you?', blank=True, default=None, null=True, max_length=8)),
                ('wait_time', models.CharField(max_length=12, help_text='How long did you wait for the service to be delivered, after contacting the service provider?', choices=[('lesshour', 'Less than 1 hour'), ('uptotwodays', '1-48 hours'), ('3-7days', '3-7 days'), ('1-2weeks', '1-2 weeks'), ('more', 'More than 2 weeks')], blank=True, null=True, default=None)),
                ('wait_time_satisfaction', models.SmallIntegerField(help_text='How do you rate your satisfaction with the time that you waited for the service to be delivered (from 1 to 5, where 5 is the highest rating possible)?', null=True, blank=True, default=None, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('difficulty_contacting', models.CharField(max_length=20, help_text='Did you experience difficulties contacting the provider of the service you needed?', choices=[('didntknow', 'Did not know how to contact them'), ('nophoneresponse', 'Tried to contact them by phone but received no response'), ('noresponse', 'Tried to contact them in person but received no response or did not find their office'), ('unhelpful', 'Contacted them but response was unhelpful'), ('other', 'Other')])),
                ('other_difficulties', models.TextField(help_text='Other difficulties contacting the service provider', blank=True, default='')),
                ('staff_satisfaction', models.SmallIntegerField(help_text='How would you rate your satisfaction with the staff of the organization that provided services to you, (from 1 to 5, where 5 is the highest rating possible)?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('extra_comments', models.TextField(help_text='Other comments', blank=True, default='')),
                ('anonymous', models.BooleanField(help_text='I want my feedback to be anonymous to the service provider', default=False)),
                ('area_of_residence', models.ForeignKey(verbose_name='area of residence', to='services.ServiceArea')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('number', models.IntegerField(unique=True)),
                ('name_en', models.CharField(max_length=256, verbose_name='name in English', blank=True, default='')),
                ('name_ar', models.CharField(max_length=256, verbose_name='name in Arabic', blank=True, default='')),
                ('name_fr', models.CharField(max_length=256, verbose_name='name in French', blank=True, default='')),
            ],
            options={
            },
            bases=(services.models.NameInCurrentLanguageMixin, models.Model),
        ),
        migrations.AddField(
            model_name='feedback',
            name='nationality',
            field=models.ForeignKey(verbose_name='nationality', to='services.Nationality'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedback',
            name='service',
            field=models.ForeignKey(verbose_name='service', to='services.Service'),
            preserve_default=True,
        ),
    ]
