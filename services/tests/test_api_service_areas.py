from http.client import OK
import json
from django.core.urlresolvers import reverse
from django.test import TestCase
from services.models import ServiceArea
from services.tests.factories import ServiceAreaFactory
from services.tests.test_api import APITestMixin


class ServiceAreaAPITest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        ServiceArea.objects.all().delete()
        # Area 1 will be a parent
        self.area1 = ServiceAreaFactory()
        # 2 & 3 will be children of that parent and therefore lowest-level areas
        self.area2 = ServiceAreaFactory(parent=self.area1)
        self.area3 = ServiceAreaFactory(parent=self.area1)
        # 4 is not a parent of anything so also a lowest-level area
        self.area4 = ServiceAreaFactory()

    def test_get_areas(self):
        # Should get all, whether top-level or not
        rsp = self.get_with_token(reverse('servicearea-list'))
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        results = result
        result_names = [item['name_en'] for item in results]
        self.assertIn(self.area1.name_en, result_names)
        self.assertIn(self.area2.name_en, result_names)
        self.assertIn(self.area3.name_en, result_names)
        self.assertIn(self.area4.name_en, result_names)

    def test_get_area(self):
        rsp = self.get_with_token(self.area2.get_api_url())
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(self.area2.id, result['id'])
        self.assertEqual('http://testserver%s' % self.area1.get_api_url(), result['parent'])
