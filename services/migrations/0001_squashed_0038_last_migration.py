# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
import django.contrib.gis.db.models.fields
import services.models
import os
from django.conf import settings
from django.db import models, migrations
from services.utils import update_postgres_sequence_generator
from services.utils import permission_names_to_objects



INITIAL_PROVIDER_TYPES = [
    dict(number=1, name_en="Local NGO", name_ar="منظمة غير حكومية محلية"),
    dict(number=2, name_en="International NGO", name_ar="منظمة غير حكومية عالمية"),
    dict(number=3, name_en="Public Hospitals", name_ar="مستشفيات حكومية"),
    dict(number=4, name_en="Public Schools", name_ar="مدارس رسمية"),
    dict(number=5, name_en="Private Hospitals", name_ar="مستشفيات خاصة"),
    dict(number=6, name_en="Private Schools", name_ar="مدارس خاصة"),
    dict(number=7, name_en="Community Centers", name_ar="مراكز إجتماعية"),
    dict(number=8, name_en="UN Agency", name_ar="وكالة الأمم المتحدة"),
]


def no_op(apps, schema_editor):
    pass


def create_provider_types(apps, schema_editor):
    ProviderType = apps.get_model('services', 'ProviderType')
    for value in INITIAL_PROVIDER_TYPES:
        ProviderType.objects.get_or_create(
            number=value['number'],
            defaults=value,
        )


def define_sites(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # These names changed after the initial migration (0008) was run,
    # so make sure they're updated now.
    Site.objects.update_or_create(
        id=settings.DEV_SITE_ID,
        defaults=dict(
            name='IRC Service Info Dev',
            domain='localhost:8000',
        )
    )
    Site.objects.update_or_create(
        id=settings.STAGING_SITE_ID,
        defaults=dict(
            name='IRC Service Info Staging',
            domain='serviceinfo-staging.rescue.org',
        )
    )
    Site.objects.update_or_create(
        id=settings.PRODUCTION_SITE_ID,
        defaults=dict(
            name='IRC Service Info',
            domain='serviceinfo.rescue.org',
        )
    )


INITIAL_SERVICE_TYPES = [
    dict(number=1, name_en='Education Services', name_ar='خدمات التعليم'),
    dict(number=2, name_en='Health Services', name_ar='الخدمات الصحية',
         comments_en='including psychosocial and disabilities'),
    dict(number=3, name_en='Shelter & Wash Services', name_ar='المأوى وخدمات الصرف الصحي والنظافة',
         comments_en='including shelter rehabilitation'),
    dict(number=4, name_en='Financial services', name_ar='الخدمات المالية',
         comments_en='including unconditional cash assistance'),
    dict(number=5, name_en='Legal services', name_ar='الخدمات القانونية'),
    dict(number=6, name_en='Food Security', name_ar='الإعاشات الغذائية'),
    dict(number=7, name_en='Material Support (excluding cash and food)',
         name_ar='المساعدات العينية الغير غذائية والغير مالية'),
    dict(number=8, name_en='Community centers', name_ar='المراكز الإجتماعية',
         comments_en='including vocational trainings and awareness sessions'),
]


def create_service_types(apps, schema_editor):
    ServiceType = apps.get_model('services', 'ServiceType')
    for value in INITIAL_SERVICE_TYPES:
        ServiceType.objects.get_or_create(
            number=value['number'],
            defaults=value,
        )



# Permissions needed by staff
# Permission names are "applabel.action_lowercasemodelname"
STAFF_PERMISSIONS = [
    'services.change_provider',
    'services.change_service',
    'services.change_selectioncriterion',
]

# Typical provider permissions
PROVIDER_PERMISSIONS = [
    'services.add_provider',
    'services.change_provider',
    'services.add_service',
    'services.change_service',
    'services.add_selectioncriterion',
    'services.change_selectioncriterion',
]


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    group, unused = Group.objects.get_or_create(name='Staff')
    group.permissions.add(*permission_names_to_objects(STAFF_PERMISSIONS, Permission, ContentType))

    group, unused = Group.objects.get_or_create(name='Providers')
    group.permissions.add(*permission_names_to_objects(PROVIDER_PERMISSIONS, Permission, ContentType))


MOUNT_LEBANON = 'Mount Lebanon'
TRIPOLI = 'Tripoli and surroundings'
INITIAL_AREAS = [
    # Numbers are arbitrary, just so we can know which ones we created and remove
    # them again or at least not duplicate them if we migrate forward and back.
    (1, MOUNT_LEBANON, "Baabda", "بعبدا"),
    (2, MOUNT_LEBANON, "Beirut", "بيروت"),
    (3, MOUNT_LEBANON, "Aley", "عاليه"),
    (4, MOUNT_LEBANON, "Chouf", "الشوف"),
    (5, MOUNT_LEBANON, "Keserwane", "كسروان"),
    (6, MOUNT_LEBANON, "El-Metn", "المتن"),
    (7, MOUNT_LEBANON, "Jbeil", "جبيل"),

    (21, TRIPOLI, "Mineih-Dinniyi", "المنيه-الضنية"),
    (22, TRIPOLI, "Zgharta", "زغرتا"),
    (23, TRIPOLI, "Bcharri", "بشري"),
    (24, TRIPOLI, "Tripoli", "طرابلس"),
    (25, TRIPOLI, "Koura", "الكورة"),
    (26, TRIPOLI, "Batroun", "البترون"),

]


def create_areas(apps, schema_editor):
    ServiceArea = apps.get_model('services', 'ServiceArea')

    for number, parent, english, arabic in INITIAL_AREAS:
        # If the area already exists, do not change it because someone might
        # have edited it and we don't want to lose their changes.
        ServiceArea.objects.get_or_create(
            pk=number,
            defaults=dict(
                name_en="%s / %s" % (parent, english),
                name_ar="%s / %s" % (parent, arabic),
            )
        )
    update_postgres_sequence_generator(ServiceArea)

from django.core.files import File

st_icon_image_names = (
    (1, 'education_64px.png'),
    (2, 'health_64px.png'),
    (3, 'wash_shower_64px.png'),
    (4, 'financing_64px.png'),
    (5, 'law_64px.png'),
    (6, 'food_NFI_food_64px.png'),
    (7, 'nonfood_support_item_64px.png'),
    (8, 'community_building_64px.png'),
)

EXISTING_ICON_DIRECTORY = os.path.join(settings.PROJECT_ROOT, 'frontend', 'images')


def populate_service_icons(apps, schema_editor):
    ServiceType = apps.get_model('services', 'ServiceType')
    for st_number, icon_fname in st_icon_image_names:
        icon_file = open(os.path.join(EXISTING_ICON_DIRECTORY, icon_fname), 'rb')
        service_type = ServiceType.objects.get(number=st_number)
        service_type.icon.save(icon_fname, File(icon_file))

INITIAL_NATIONALITIES = [
    dict(number=1, name_en='Lebanese', name_ar='لبناني'),
    dict(number=2, name_en='Lebanese returnees from Syria', name_ar='لبناني عائد من سوريا'),
    dict(number=3, name_en='Palestine refugees in Lebanon', name_ar='فلسطيني مقيم في لبنان'),
    dict(number=4, name_en='Palestine refugees from Syria', name_ar='فلسطيني عائد من سوريا'),
    dict(number=5, name_en='Syrian', name_ar='سوري'),
    dict(number=6, name_en='Iraqi', name_ar='عراقي'),
    dict(number=7, name_en='Other', name_ar='جنسيات أخرى'),
]



def create_nationalities(apps, schema_editor):
    Nationality = apps.get_model('services', 'Nationality')
    for value in INITIAL_NATIONALITIES:
        Nationality.objects.get_or_create(
            number=value['number'],
            defaults=value,
        )


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# services.migrations.0038_last_migration

class Migration(migrations.Migration):

    replaces = [('services', '0001_initial'), ('services', '0002_auto_20150112_0951'), ('services', '0003_auto_20150112_1106'), ('services', '0004_auto_20150112_1109'), ('services', '0005_rename_english_fields'), ('services', '0006_add_non_english_fields'), ('services', '0007_update_service_fields'), ('services', '0008_add_sites'), ('services', '0009_auto_20150127_1348'), ('services', '0010_create_service_types'), ('services', '0009_selectioncriterion_provider'), ('services', '0011_merge'), ('services', '0012_remove_selectioncriterion_provider'), ('services', '0011_providertype_number'), ('services', '0012_providertypes'), ('services', '0013_merge'), ('services', '0014_auto_20150130_1431'), ('services', '0011_auto_20150129_1534'), ('services', '0015_merge'), ('services', '0016_selectioncriterion_service'), ('services', '0016_auto_20150204_1720'), ('services', '0017_merge'), ('services', '0016_groups'), ('services', '0018_merge'), ('services', '0019_fix_production_site_domain'), ('services', '0020_auto_20150209_2237'), ('services', '0021_auto_20150212_1935'), ('services', '0022_auto_20150213_1637'), ('services', '0021_populate_areas'), ('services', '0023_merge'), ('services', '0024_auto_20150225_1442'), ('services', '0024_auto_20150224_2352'), ('services', '0025_merge'), ('services', '0026_auto_20150302_2222'), ('services', '0027_auto_20150310_1501'), ('services', '0027_auto_20150306_1502'), ('services', '0028_merge'), ('services', '0029_auto_20150311_1423'), ('services', '0028_group_permissions'), ('services', '0030_merge'), ('services', '0031_servicetype_icon'), ('services', '0032_auto_20150312_1536'), ('services', '0033_auto_20150316_1542'), ('services', '0034_create_nationalities'), ('services', '0035_auto_20150325_1637'), ('services', '0036_auto_20150327_1434'), ('services', '0037_auto_20150505_1742'), ('services', '0038_last_migration')]

    dependencies = [
        ('auth', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(blank=True, max_length=256, default='', verbose_name='name in English')),
                ('name_fr', models.CharField(blank=True, max_length=256, default='', verbose_name='name in French')),
                ('name_ar', models.CharField(blank=True, max_length=256, default='', verbose_name='name in Arabic')),
                ('number', models.IntegerField(unique=True, default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(blank=True, max_length=256, default='', verbose_name='name in English')),
                ('type', models.ForeignKey(to='services.ProviderType', verbose_name='type')),
                ('phone_number', models.CharField(max_length=20, verbose_name='phone number')),
                ('website', models.URLField(blank=True, default='', verbose_name='website')),
                ('description_en', models.TextField(blank=True, default='', verbose_name='description in English')),
                ('user', models.OneToOneField(help_text='user account for this provider', default=1, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('description_ar', models.TextField(blank=True, default='', verbose_name='description in Arabic')),
                ('description_fr', models.TextField(blank=True, default='', verbose_name='description in French')),
                ('name_ar', models.CharField(blank=True, max_length=256, default='', verbose_name='name in Arabic')),
                ('name_fr', models.CharField(blank=True, max_length=256, default='', verbose_name='name in French')),
                ('number_of_monthly_beneficiaries', models.IntegerField(default=0, verbose_name='number of targeted beneficiaries monthly')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SelectionCriterion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('hours_of_service', models.TextField(verbose_name='hours of service')),
                ('additional_info', models.TextField(blank=True, default='', verbose_name='additional info')),
                ('cost_of_service', models.TextField(blank=True, default='', verbose_name='cost of service')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceArea',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(blank=True, max_length=256, default='', verbose_name='name in English')),
                ('parent', models.ForeignKey(help_text='the area that contains this area', blank=True, null=True, related_name='children', to='services.ServiceArea', verbose_name='parent area')),
                ('region', django.contrib.gis.db.models.fields.PolygonField(blank=True, srid=4326, null=True)),
                ('name_ar', models.CharField(blank=True, max_length=256, default='', verbose_name='name in Arabic')),
                ('name_fr', models.CharField(blank=True, max_length=256, default='', verbose_name='name in French')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='area_of_service',
            field=models.ForeignKey(to='services.ServiceArea', verbose_name='area of service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='provider',
            field=models.ForeignKey(to='services.Provider', verbose_name='provider'),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='selectioncriterion',
            options={'verbose_name_plural': 'selection criteria'},
        ),
        migrations.AddField(
            model_name='service',
            name='status',
            field=models.CharField(max_length=10, choices=[('draft', 'draft'), ('current', 'current'), ('rejected', 'rejected'), ('canceled', 'canceled'), ('archived', 'archived')], default='draft', verbose_name='status'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='update_of',
            field=models.ForeignKey(help_text='If a service record represents a modification of an existing service record that is still pending approval, this field links to the existing service record.', unique=True, blank=True, null=True, related_name='pending_update', to='services.Service'),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='service',
            old_name='additional_info',
            new_name='additional_info_en',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='description',
            new_name='description_en',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='name',
            new_name='name_en',
        ),
        migrations.AddField(
            model_name='service',
            name='additional_info_ar',
            field=models.TextField(blank=True, default='', verbose_name='additional information in Arabic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='additional_info_fr',
            field=models.TextField(blank=True, default='', verbose_name='additional information in French'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='description_ar',
            field=models.TextField(blank=True, default='', verbose_name='description in Arabic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='description_fr',
            field=models.TextField(blank=True, default='', verbose_name='description in French'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='name_ar',
            field=models.CharField(blank=True, max_length=256, default='', verbose_name='name in Arabic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='name_fr',
            field=models.CharField(blank=True, max_length=256, default='', verbose_name='name in French'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='additional_info_en',
            field=models.TextField(blank=True, default='', verbose_name='additional information in English'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='description_en',
            field=models.TextField(verbose_name='description in English'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='name_en',
            field=models.CharField(blank=True, max_length=256, default='', verbose_name='name in English'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='service',
            name='hours_of_service',
        ),
        migrations.AddField(
            model_name='selectioncriterion',
            name='text_ar',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selectioncriterion',
            name='text_en',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='selectioncriterion',
            name='text_fr',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='friday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='friday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, srid=4326, null=True, verbose_name='location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='monday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='monday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='saturday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='saturday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='sunday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='sunday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='thursday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='thursday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='tuesday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='tuesday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='wednesday_close',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='wednesday_open',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='description_en',
            field=models.TextField(blank=True, default='', verbose_name='description in English'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
                ('name_en', models.CharField(blank=True, max_length=256, default='', verbose_name='name in English')),
                ('name_ar', models.CharField(blank=True, max_length=256, default='', verbose_name='name in Arabic')),
                ('name_fr', models.CharField(blank=True, max_length=256, default='', verbose_name='name in French')),
                ('comments_en', models.CharField(blank=True, max_length=512, default='', verbose_name='comments in English')),
                ('comments_ar', models.CharField(blank=True, max_length=512, default='', verbose_name='comments in Arabic')),
                ('comments_fr', models.CharField(blank=True, max_length=512, default='', verbose_name='comments in French')),
                ('icon', models.ImageField(blank=True, upload_to='service-type-icons', verbose_name='icon')),
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
        migrations.AddField(
            model_name='selectioncriterion',
            name='service',
            field=models.ForeignKey(related_name='selection_criteria', to='services.Service'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='JiraUpdateRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('update_type', models.CharField(max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service')], verbose_name='update type')),
                ('jira_issue_key', models.CharField(blank=True, max_length=256, default='', verbose_name='JIRA issue')),
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
        migrations.AlterField(
            model_name='service',
            name='update_of',
            field=models.ForeignKey(help_text='If a service record represents a modification of an existing service record that is still pending approval, this field links to the existing service record.', related_name='pending_update', blank=True, null=True, to='services.Service'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service')], verbose_name='update type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='superseded_draft',
            field=models.ForeignKey(blank=True, null=True, to='services.Service'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft')], verbose_name='update type'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='phone_number',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], max_length=20, verbose_name='phone number'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='number_of_monthly_beneficiaries',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000)], null=True, verbose_name='number of targeted beneficiaries monthly'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_ar',
            field=models.CharField(blank=True, validators=[services.models.blank_or_at_least_one_letter], default='', max_length=256, verbose_name='name in Arabic'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_en',
            field=models.CharField(blank=True, validators=[services.models.blank_or_at_least_one_letter], default='', max_length=256, verbose_name='name in English'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_fr',
            field=models.CharField(blank=True, validators=[services.models.blank_or_at_least_one_letter], default='', max_length=256, verbose_name='name in French'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='address_ar',
            field=models.TextField(blank=True, default='', verbose_name='provider address in Arabic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='address_en',
            field=models.TextField(blank=True, default='', verbose_name='provider address in English'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='address_fr',
            field=models.TextField(blank=True, default='', verbose_name='provider address in French'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_name_ar',
            field=models.CharField(blank=True, validators=[services.models.blank_or_at_least_one_letter], default='', max_length=256, verbose_name='focal point name in Arabic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_name_en',
            field=models.CharField(blank=True, validators=[services.models.blank_or_at_least_one_letter], default='', max_length=256, verbose_name='focal point name in English'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_name_fr',
            field=models.CharField(blank=True, validators=[services.models.blank_or_at_least_one_letter], default='', max_length=256, verbose_name='focal point name in French'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='focal_point_phone_number',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], default='', max_length=20, verbose_name='focal point phone number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='by',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft'), ('approve-service', 'Staff approved a new or changed service'), ('rejected-service', 'Staff rejected a new or changed service')], verbose_name='update type'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='service',
            name='update_of',
            field=models.ForeignKey(help_text='If a service record represents a modification of another service record, this field links to that other record.', related_name='updates', blank=True, null=True, to='services.Service'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], max_length=20, verbose_name='phone number')),
                ('delivered', models.BooleanField(help_text='Was the service you sought delivered to you?', default=False)),
                ('quality', models.SmallIntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], null=True, default=None, help_text='How would you rate the quality of the service you received (from 1 to 5, where 5 is the highest rating possible)?')),
                ('non_delivery_explained', models.CharField(help_text='Did you receive a clear explanation for why the service you sought was not delivered to you?', max_length=8, choices=[('no', 'No explanation'), ('unclear', 'Explanation was not clear'), ('unfair', 'Explanation was not fair'), ('yes', 'Clear and appropriate explanation')], default=None, blank=True, null=True)),
                ('wait_time', models.CharField(help_text='How long did you wait for the service to be delivered, after contacting the service provider?', max_length=12, choices=[('lesshour', 'Less than 1 hour'), ('uptotwodays', '1-48 hours'), ('3-7days', '3-7 days'), ('1-2weeks', '1-2 weeks'), ('more', 'More than 2 weeks')], default=None, blank=True, null=True)),
                ('wait_time_satisfaction', models.SmallIntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], null=True, default=None, help_text='How do you rate your satisfaction with the time that you waited for the service to be delivered (from 1 to 5, where 5 is the highest rating possible)?')),
                ('difficulty_contacting', models.CharField(help_text='Did you experience difficulties contacting the provider of the service you needed?', max_length=20, choices=[('didntknow', 'Did not know how to contact them'), ('nophoneresponse', 'Tried to contact them by phone but received no response'), ('noresponse', 'Tried to contact them in person but received no response or did not find their office'), ('unhelpful', 'Contacted them but response was unhelpful'), ('other', 'Other')])),
                ('other_difficulties', models.TextField(blank=True, help_text='Other difficulties contacting the service provider', default='')),
                ('staff_satisfaction', models.SmallIntegerField(help_text='How would you rate your satisfaction with the staff of the organization that provided services to you, (from 1 to 5, where 5 is the highest rating possible)?', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('extra_comments', models.TextField(blank=True, help_text='Other comments', default='')),
                ('anonymous', models.BooleanField(help_text='I want my feedback to be anonymous to the service provider', default=False)),
                ('area_of_residence', models.ForeignKey(to='services.ServiceArea', verbose_name='area of residence')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
                ('name_en', models.CharField(blank=True, max_length=256, default='', verbose_name='name in English')),
                ('name_ar', models.CharField(blank=True, max_length=256, default='', verbose_name='name in Arabic')),
                ('name_fr', models.CharField(blank=True, max_length=256, default='', verbose_name='name in French')),
            ],
            options={
            },
            bases=(services.models.NameInCurrentLanguageMixin, models.Model),
        ),
        migrations.AddField(
            model_name='feedback',
            name='nationality',
            field=models.ForeignKey(to='services.Nationality', verbose_name='Nationality'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedback',
            name='service',
            field=models.ForeignKey(to='services.Service', verbose_name='Service'),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='nationality',
            options={'verbose_name_plural': 'nationalities'},
        ),
        migrations.AlterField(
            model_name='feedback',
            name='difficulty_contacting',
            field=models.CharField(help_text='Did you experience difficulties contacting the provider of the service you needed?', max_length=20, choices=[('no', 'No'), ('didntknow', 'Did not know how to contact them'), ('nophoneresponse', 'Tried to contact them by phone but received no response'), ('noresponse', 'Tried to contact them in person but received no response or did not find their office'), ('unhelpful', 'Contacted them but response was unhelpful'), ('other', 'Other')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jiraupdaterecord',
            name='feedback',
            field=models.ForeignKey(related_name='jira_records', blank=True, null=True, to='services.Feedback'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jiraupdaterecord',
            name='update_type',
            field=models.CharField(max_length=22, choices=[('provider-change', 'Provider updated their information'), ('new-service', 'New service submitted by provider'), ('change-service', 'Change to existing service submitted by provider'), ('cancel-draft-service', 'Provider canceled a draft service'), ('cancel-current-service', 'Provider canceled a current service'), ('superseded-draft', 'Provider superseded a previous draft'), ('approve-service', 'Staff approved a new or changed service'), ('rejected-service', 'Staff rejected a new or changed service'), ('feedback', 'User submitted feedback')], verbose_name='update type'),
            preserve_default=True,
        ),
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
            name='phone_number',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^\\d{2}-\\d{6}$')], max_length=20, verbose_name='Phone Number (NN-NNNNNN)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='wait_time',
            field=models.CharField(help_text='How long did you wait for the service to be delivered, after contacting the service provider?', max_length=12, choices=[('lesshour', 'Less than 1 hour'), ('uptotwodays', 'Up to 2 days'), ('3-7days', '3-7 days'), ('1-2weeks', '1-2 weeks'), ('more', 'More than 2 weeks')], default=None, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=define_sites,
            reverse_code=no_op,
            atomic=True,
        ),
        migrations.RunPython(
            code=create_nationalities,
            reverse_code=no_op,
            atomic=True,
        ),
        migrations.RunPython(
            code=create_provider_types,
            reverse_code=no_op,
            atomic=True,
        ),
        migrations.RunPython(
            code=create_service_types,
            reverse_code=no_op,
            atomic=True,
        ),
        migrations.RunPython(
            code=create_groups,
            reverse_code=no_op,
            atomic=True,
        ),
        migrations.RunPython(
            code=create_areas,
            reverse_code=no_op,
            atomic=True,
        ),
        migrations.RunPython(
            code=populate_service_icons,
            reverse_code=no_op,
            atomic=True,
        ),
    ]
