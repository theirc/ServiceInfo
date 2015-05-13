# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.conf import settings
from django.db import models, migrations, connection
from django.db.models import Max
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
    'services.change_service'
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


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Staff', 'Providers']).delete()


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

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__first__'),
        ('sites', '0001_initial'),
        ('services', '0037_auto_20150505_1742'),
    ]

    operations = [
        migrations.RunPython(define_sites, no_op),
        migrations.RunPython(create_provider_types, no_op),
        migrations.RunPython(create_groups, no_op),
        migrations.RunPython(create_areas, no_op),
        migrations.RunPython(populate_service_icons, no_op),
        migrations.RunPython(create_nationalities, no_op),
    ]
