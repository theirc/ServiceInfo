from django.test import TestCase

from services.tests.factories import ServiceFactory
from services.models import Service
from services.search_indexes import ServiceIndex


class IndexingTest(TestCase):

    def setUp(self):
        self.service_ar = ServiceFactory(
            name_ar='Arabic', name_en='', name_fr='',
            description_ar='language-of-Egypt',
            status=Service.STATUS_CURRENT
        )
        self.service_ar.save()
        self.service_en = ServiceFactory(
            name_en='English', name_ar='', name_fr='',
            description_en='language-of-Australia',
            status=Service.STATUS_CURRENT
        )
        self.service_en.save()
        self.service_fr = ServiceFactory(
            name_fr='French', name_ar='', name_en='',
            description_fr='language-of-France',
            status=Service.STATUS_CURRENT
        )
        self.service_fr.save()
        self.rejected_service_fr = ServiceFactory(
            name_fr='InactiveParis', name_ar='', name_en='',
            status=Service.STATUS_REJECTED
        )
        self.rejected_service_fr.save()

    def test_querysets(self):
        index = ServiceIndex()
        self.assertIn(self.service_ar, index.get_index_queryset('ar'))
        self.assertNotIn(self.service_ar, index.get_index_queryset('en'))

        self.assertIn(self.service_fr, index.get_index_queryset('fr'))
        self.assertNotIn(self.service_fr, index.get_index_queryset('ar'))

        self.assertNotIn(self.rejected_service_fr, index.get_index_queryset('fr'))

    def test_search_data(self):
        index = ServiceIndex()
        ar_data = index.get_search_data(self.service_ar, 'ar', None)
        self.assertIn('Egypt', ar_data)
        en_data = index.get_search_data(self.service_en, 'en', None)
        self.assertIn('Australia', en_data)
