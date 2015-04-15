from http.client import OK
import json
from django.test import TestCase
from services.models import Service
from services.tests.factories import ServiceFactory
from services.tests.test_api import APITestMixin


class PaginationTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = '/api/services/search/'

    def test_services_not_paginated_by_default(self):
        # Make sure that we don't paginate by default when the caller might
        # not be expecting it.

        # Create over 100 services - hopefully any default would tend to be
        # less than that.
        for x in range(101):
            ServiceFactory(status=Service.STATUS_CURRENT)
        rsp = self.client.get(self.url)  # not authed
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(Service.objects.filter(status=Service.STATUS_CURRENT).count(),
                         len(response))

    def test_services_pagination(self):
        # We can paginate the service search results
        for x in range(10):
            ServiceFactory(status=Service.STATUS_CURRENT)
        rsp = self.client.get(self.url + "?limit=5")  # not authed
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        records_returned = response['results']
        self.assertEqual(5, len(records_returned))
        first_five = records_returned
        rsp = self.client.get(self.url + "?limit=5&offset=5")  # not authed
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        records_returned = response['results']
        self.assertEqual(5, len(records_returned))
        last_five = records_returned
        records_in_both = set(r['id'] for r in first_five) & set(r['id'] for r in last_five)
        self.assertFalse(records_in_both)
