# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0015_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='JiraUpdateRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('update_type', models.CharField(verbose_name='update type', choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service')], max_length=22)),
                ('jira_issue_key', models.CharField(blank=True, verbose_name='JIRA issue', default='', max_length=256)),
                ('provider', models.ForeignKey(related_name='jira_records', blank=True, null=True, to='services.Provider')),
                ('service', models.ForeignKey(related_name='jira_records', blank=True, null=True, to='services.Service')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='jiraupdaterecord',
            unique_together=set([('service', 'update_type')]),
        ),
    ]
