# Make sure our GEO data is loaded
from django.test import TestCase
from services.models import LebanonRegion, ServiceArea


class GeoTestCase(TestCase):
    def test_we_have_regions(self):
        self.assertTrue(LebanonRegion.objects.all().exists())

    def test_level_two_regions_have_parents(self):
        self.assertFalse(LebanonRegion.objects.filter(level=2, parent=None).exists())

    def test_service_areas_have_regions(self):
        self.assertFalse(ServiceArea.objects.filter(lebanon_region=False).exists())
