from http.client import CREATED, BAD_REQUEST, METHOD_NOT_ALLOWED, NOT_FOUND
from django.forms import model_to_dict
from django.test import TestCase
from services.models import ServiceArea, ServiceType, RequestForService
from services.tests.factories import RequestForServiceFactory
from services.tests.test_api import APITestMixin


class RequestForServiceTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        # Do NOT need to be logged in
        self.token = None
        self.url = '/api/requestsforservice/'
        self.data = {
            'provider_name': 'Joe Provider',
            'service_name': 'Large animal veterinarian',
            'area_of_service': ServiceArea.objects.first().get_api_url(),
            'service_type': ServiceType.objects.first().get_api_url(),
            'address': """Somewhere
            Over the rainbow
            Far, far away
            """,
            'contact': """Dr. F. Frankonsteen,
            Big Castle,
            Top of the Hill
            """,
            'description': """A really
            really
            awesome service
            """,
            'rating': 3,
        }

    def test_create_request_for_service(self):
        # Basic test of creating one
        rsp = self.api_client.post(self.url, data=self.data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('UTF-8'))
        req = RequestForService.objects.get(provider_name=self.data['provider_name'])
        self.maxDiff = None
        req_data = model_to_dict(req)
        req_data['area_of_service'] = ServiceArea.objects.get(pk=req_data['area_of_service']).get_api_url()
        req_data['service_type'] = ServiceType.objects.get(pk=req_data['service_type']).get_api_url()
        del req_data['id']
        self.assertEqual(req_data, self.data)

    def test_empty_provider_name(self):
        self.data['provider_name'] = ''
        rsp = self.api_client.post(self.url, data=self.data)
        self.assertEqual(BAD_REQUEST, rsp.status_code)

    def test_cannot_list(self):
        url = '/api/requestsforservice/'
        rsp = self.api_client.get(url)
        self.assertEqual(METHOD_NOT_ALLOWED, rsp.status_code)

    def test_cannot_get_detail(self):
        req = RequestForServiceFactory()
        url = '/api/requestsforservice/%d/' % req.pk
        rsp = self.api_client.get(url)
        self.assertEqual(NOT_FOUND, rsp.status_code)
