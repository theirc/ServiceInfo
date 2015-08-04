from http.client import OK
import json
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.test import TestCase
from services.models import ServiceType
from services.tests.test_api import APITestMixin


class ServiceTypeAPITest(APITestMixin, TestCase):
    def test_get_types(self):
        rsp = self.get_with_token(reverse('servicetype-list'))
        self.assertEqual(OK, rsp.status_code)
        results = json.loads(rsp.content.decode('utf-8'))
        result = results[0]
        self.assertIn('icon_url', result)
        icon_url = result['icon_url']
        self.assertTrue(icon_url.startswith(settings.MEDIA_URL))
        path = icon_url.replace(settings.MEDIA_URL, '')
        self.assertTrue(default_storage.exists(path))

    def test_get_type(self):
        # Try it unauthenticated
        a_type = ServiceType.objects.first()
        url = a_type.get_api_url()
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertIn('icon_url', result)
        icon_url = result['icon_url']
        self.assertTrue(icon_url.startswith(settings.MEDIA_URL))
        path = icon_url.replace(settings.MEDIA_URL, '')
        self.assertTrue(default_storage.exists(path))
