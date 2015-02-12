# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connection
from django.db.models import Max


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


def update_postgres_sequence_generator(model):
    """
    Update the sequence generator for a model's primary key
    to the max current value of that key, so that Postgres
    will know not to try to use the previously-used values again.

    Apparently this is needed because when we create objects
    during the migration, we specify the primary key's value,
    so the Postgres sequence doesn't get used or incremented.
    """
    table_name = model._meta.db_table
    attname, colname = model._meta.pk.get_attname_column()
    seq_name = "%s_%s_seq" % (table_name, colname)
    max_val = model.objects.aggregate(maxkey=Max(attname))['maxkey']
    cursor = connection.cursor()
    cursor.execute("select setval(%s, %s);", [seq_name, max_val])


def no_op(apps, schema_editor):
    # When we back up the migration, don't remove any records.
    pass

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


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0020_auto_20150209_2237'),
    ]

    operations = [
        migrations.RunPython(create_areas, no_op),
    ]


"""

Number
Mount Lebanon
Tripoli and surroundings
1
Baabda بعبدا
Mineih-Dinniyiالمنيه-الضنية
2
Beirutبيروت
Zghartaزغرتا
3
Aleyعاليه
Bcharriبشري
4
Choufالشوف
Tripoliطرابلس
5
Keserwaneكسروان
Kouraالكورة
6
El-Metnالمتن
 Batroun البترون
7
Jbeilجبيل


"""
