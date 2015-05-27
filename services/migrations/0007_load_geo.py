# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping

from django.db import models, migrations


# map the field names in our LebanonRegion model to the geo fields in level 1
from django.utils.encoding import force_text


lebanonlevel1_mapping = {
    'area' : 'AREA',
    'perimeter' : 'PERIMETER',
    'moh_na' : 'Moh_NA_I',
    'moh_cod' : 'MOH_COD',
    'shape_leng' : 'Shape_Leng',
    'shape_area' : 'Shape_Area',
    'geom' : 'POLYGON',
    'name': 'Moh_NA_I',
    'code': 'MOH_COD',
}

# map the field names in our LebanonRegion model to the geo fields in level 2
lebanonlevel2_mapping = {
    'area' : 'AREA',
    'perimeter' : 'PERIMETER',
    'moh_na' : 'MOH_NA',
    'kadaa_code' : 'Kadaa_Code',
    'kada_name' : 'Kada_Name',
    'shape_leng' : 'Shape_Leng',
    'shape_area' : 'Shape_Area',
    'moh_cod' : 'MOH_COD',
    'geom' : 'MULTIPOLYGON',
    'name': 'CAZA_NA',
    'code': 'Kadaa_Code',
}



# These were the initial service areas
# MOUNT_LEBANON = 'Mount Lebanon'
# TRIPOLI = 'Tripoli and surroundings'
# INITIAL_AREAS = [
#     # Numbers are arbitrary, just so we can know which ones we created and remove
#     # them again or at least not duplicate them if we migrate forward and back.
#     (1, MOUNT_LEBANON, "Baabda", "بعبدا"),
#     (2, MOUNT_LEBANON, "Beirut", "بيروت"),
#     (3, MOUNT_LEBANON, "Aley", "عاليه"),
#     (4, MOUNT_LEBANON, "Chouf", "الشوف"),
#     (5, MOUNT_LEBANON, "Keserwane", "كسروان"),
#     (6, MOUNT_LEBANON, "El-Metn", "المتن"),
#     (7, MOUNT_LEBANON, "Jbeil", "جبيل"),
#
#     (21, TRIPOLI, "Mineih-Dinniyi", "المنيه-الضنية"),
#     (22, TRIPOLI, "Zgharta", "زغرتا"),
#     (23, TRIPOLI, "Bcharri", "بشري"),
#     (24, TRIPOLI, "Tripoli", "طرابلس"),
#     (25, TRIPOLI, "Koura", "الكورة"),
#     (26, TRIPOLI, "Batroun", "البترون"),
# ]
# Then we added top-level areas
#   27  Mount Lebanon
#   28  Tripoli and surroundings

# map from level, name to an area index, so we can point the original service areas
# at the correct new LebanonRegion records
map_to_area = {
    (1, "Mount Lebanon"): 27,  # Mount Lebanon
    (1, "North"): 28,  # Tripoli and surroundings
    (2, "Baabda"): 1,
    (2, "Beyrouth"): 2,
    (2, "Aley"): 3,
    (2, "Chouf"): 4,
    (2, "Kesrouane"): 5,
    (2, "El Metn"): 6,
    (2, "Jbail"): 7,
    (2, "Minié-Danniyé"): 21,
    (2, "Zgharta"): 22,
    (2, "Bcharré"): 23,
    (2, "Tripoli"): 24,
    (2, "Koura"): 25,
    (2, "Batroun"): 26,
}

data_dir = os.path.join(settings.PROJECT_ROOT, 'data')


class CustomLayerMapping(LayerMapping):
    """
    Customized LayerMapping class that helps us set the 'level'
    field on the imported records.
    """
    def __init__(self, *args, **kwargs):
        self.level = kwargs.pop('level')
        super().__init__(*args, **kwargs)

    def feature_kwargs(self, feat):
        kwargs = super().feature_kwargs(feat)
        kwargs['level'] = self.level
        return kwargs


def remove_regions(apps, schema_editor):
    LebanonRegion = apps.get_model('services', 'LebanonRegion')
    LebanonRegion.objects.all().delete()


def load_geo(apps, schema_editor):
    LebanonRegion = apps.get_model('services', 'LebanonRegion')
    ServiceArea = apps.get_model('services', 'ServiceArea')

    # We'll load the first two levels of shapefiles
    shapefiles = [
        (1, 'Lebanon_Admin_1/lbn_adm1_ply.shp', lebanonlevel1_mapping),
        (2, 'Lebanon_Admin_2/lbn_adm2_ply.shp', lebanonlevel2_mapping),
    ]

    for level, filename, mapping in shapefiles:
        shp = os.path.abspath(os.path.join(data_dir, filename))
        lm = CustomLayerMapping(LebanonRegion, shp, mapping, level=level,
                                transform=False, encoding='utf-8')
        lm.save(strict=True, verbose=False)

    # Link level 2 regions to their level 1 parents by matching up
    # their 'moh_cod' field values.
    for region in LebanonRegion.objects.filter(level=2):
        region.parent = LebanonRegion.objects.get(level=1, moh_cod=region.moh_cod)
        region.save()

    # Now, set regions on initial service areas
    for level, name in map_to_area.keys():
        area = ServiceArea.objects.get(pk=map_to_area[(level, name)])
        area.lebanon_region = LebanonRegion.objects.get(level=level, name=name)
        area.save()

    # We should have gotten them all.
    assert not ServiceArea.objects.filter(lebanon_region=None).exists()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_lebanon_region'),
    ]

    operations = [
        migrations.RunPython(load_geo, remove_regions),
    ]
