# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def backlink_criteria(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    SelectionCriterion = apps.get_model('services', 'SelectionCriterion')

    for criterion in SelectionCriterion.objects.filter(services=None):
        criterion.services.add(criterion.service)


def relink_criteria(apps, schema_editor):
    SelectionCriterion = apps.get_model('services', 'SelectionCriterion')

    for criterion in SelectionCriterion.objects.filter(service=None):
        service = criterion.services.first()
        if service:
            criterion.service = service
            criterion.save()
        else:
            criterion.delete()  # Orphan criterion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0015_merge'),
    ]

    operations = [
        # Add nullable FK
        migrations.AddField(
            model_name='selectioncriterion',
            name='service',
            field=models.ForeignKey(null=True, related_name='selection_criteria', to='services.Service'),
            preserve_default=True,
        ),
        # Populate FK
        migrations.RunPython(relink_criteria, backlink_criteria),
        # Remove manytomany
        migrations.RemoveField(
            model_name='service',
            name='selection_criteria',
        ),
        # Make NK not nullable
        migrations.AlterField(
            model_name='selectioncriterion',
            name='service',
            field=models.ForeignKey(related_name='selection_criteria', to='services.Service'),
            preserve_default=True,
        ),
    ]
