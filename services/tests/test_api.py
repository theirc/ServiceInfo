from http.client import FOUND
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
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

    def test_create_provider_and_user(self):
        # User is NOT logged in when creating a new provider/user
        self.client.logout()

        url = '/api/providers/create_provider/'
        data = {
            'name': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description': 'Test provider',
            'email': 'fred@example.com',
            'password': 'foobar',
        }
        rsp = self.client.post(url, data=data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))

        # Make sure they gave us back the id of the new record
        result = json.loads(rsp.content.decode('utf-8'))
        provider = Provider.objects.get(id=result['id'])
        self.assertEqual('Joe Provider', provider.name)
        user = get_user_model().objects.get(id=provider.user_id)
        self.assertFalse(user.is_active)
        self.assertTrue(user.activation_key)
        # We should have sent an activation email
        self.assertEqual(len(mail.outbox), 1)
        # with a link
        link = provider.user.get_activation_link()
        self.assertIn(link, mail.outbox[0].body)
        # user is not active
        self.assertFalse(provider.user.is_active)
        # Try activating them
        rsp = self.client.get(link, follow=False)
        self.assertEqual(FOUND, rsp.status_code, msg=rsp.content.decode('utf-8'))
        redirect_url = rsp['Location']
        if redirect_url.startswith('http://testserver'):
            redirect_url = redirect_url[len('http://testserver'):]
        self.assertEqual(settings.ACCOUNT_ACTIVATION_REDIRECT_URL, redirect_url)
        user = get_user_model().objects.get(id=provider.user_id)
        self.assertTrue(user.is_active)

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
