import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework.authtoken.models import Token

from services.models import Provider
from services.tests.factories import ProviderFactory, ProviderTypeFactory


OK = 200
CREATED = 201


class ProviderAPITest(TestCase):
    def setUp(self):
        # Just using Django auth for now
        self.user = get_user_model().objects.create_superuser(
            password='password',
            email='joe@example.com',
        )
        assert self.client.login(email='joe@example.com', password='password')

        # Get the URL of the user for the API
        self.user_url = reverse('user-detail', args=[self.user.id])

    def test_create_provider(self):
        url = reverse('provider-list')
        data = {
            'name': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description': 'Test provider',
            'user': self.user_url,
        }
        rsp = self.client.post(url, data=data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))

        # Make sure they gave us back the id of the new record
        result = json.loads(rsp.content.decode('utf-8'))
        provider = Provider.objects.get(id=result['id'])
        self.assertEqual('Joe Provider', provider.name)

    def test_get_provider_list(self):
        p1 = ProviderFactory()
        p2 = ProviderFactory()
        url = reverse('provider-list')
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        for item in result['results']:
            provider = Provider.objects.get(id=item['id'])
            self.assertIn(provider.name, [p1.name, p2.name])

    def test_get_one_provider(self):
        p1 = ProviderFactory()
        url = reverse('provider-detail', args=[p1.id])
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(p1.name, result['name'])


class TokenAuthTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            password='password',
            email='joe@example.com',
        )
        self.user_url = reverse('user-detail', args=[self.user.id])
        self.token = Token.objects.get(user=self.user).key

    def get_with_token(self, url):
        """
        Make a GET to a url, passing the token in the request headers.
        Return the response.
        """
        return self.client.get(
            url,
            HTTP_AUTHORIZATION="Token %s" % self.token
        )

    def post_with_token(self, url, data):
        return self.client.post(
            url,
            data=data,
            HTTP_AUTHORIZATION="Token %s" % self.token
        )

    def test_get_one_provider(self):
        p1 = ProviderFactory()
        url = reverse('provider-detail', args=[p1.id])
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(p1.name, result['name'])

    def test_create_provider(self):
        url = reverse('provider-list')
        data = {
            'name': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description': 'Test provider',
            'user': self.user_url,
        }
        rsp = self.post_with_token(url, data=data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))
