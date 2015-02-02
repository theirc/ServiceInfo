from http.client import OK, CREATED, BAD_REQUEST
import json

from django.contrib.auth import get_user_model, authenticate
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from email_user.models import EmailUser
from email_user.tests.factories import EmailUserFactory
from services.models import Provider, Service, SelectionCriterion
from services.tests.factories import ProviderFactory, ProviderTypeFactory, ServiceAreaFactory, \
    ServiceFactory, SelectionCriterionFactory, ServiceTypeFactory
from services.utils import permission_names_to_objects, USER_PERMISSION_NAMES


class APITestMixin(object):
    def setUp(self):
        """Return a new user who has permissions like a regular provider"""
        self.email = 'joe@example.com'
        self.password = 'password'
        self.user = get_user_model().objects.create_user(
            password=self.password,
            email=self.email,
        )
        self.user.user_permissions.add(*permission_names_to_objects(USER_PERMISSION_NAMES))
        assert self.client.login(email=self.email, password=self.password)
        # Get the URL of the user for the API
        self.user_url = reverse('user-detail', args=[self.user.id])
        self.api_client = APIClient()

    def get_with_token(self, url):
        """
        Make a GET to a url, passing self.token in the request headers.
        Return the response.
        """
        return self.api_client.get(
            url,
            HTTP_AUTHORIZATION="Token %s" % self.token
        )

    def post_with_token(self, url, data):
        """
        Make a POST to a url, passing self.token in the request headers.
        Return the response.
        """
        return self.api_client.post(
            url,
            data=data,
            HTTP_AUTHORIZATION="Token %s" % self.token,
            format='json'
        )

    def check_token(self):
        """
        Assert that the token is valid and lets the client access the API.
        """
        # Create a record that this user has access to
        p1 = ProviderFactory(user=self.user)
        url = reverse('provider-detail', args=[p1.id])
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))


class ProviderAPITest(APITestMixin, TestCase):
    def test_create_provider_no_email(self):
        # Create provider call is made when user is NOT logged in.
        self.client.logout()

        url = '/api/providers/create_provider/'
        data = {
            'name_en': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description_en': 'Test provider',
            'password': 'foobar',
            'number_of_monthly_beneficiaries': '37',
            'base_activation_link': 'https://somewhere.example.com/activate/me/?key='
        }
        rsp = self.api_client.post(url, data=data, format='json')
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        err = result['email'][0]  # Must be an email error
        # Could be different depending on whether we submitted as a form or as json
        self.assertIn(err, ['This field may not be blank.', 'This field is required.'])

    def test_create_provider_existing_email(self):
        self.client.logout()

        existing_user = EmailUserFactory()

        url = '/api/providers/create_provider/'
        data = {
            'name_en': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description_en': 'Test provider',
            'email': existing_user.email,
            'password': 'foobar',
            'number_of_monthly_beneficiaries': '37',
            'base_activation_link': 'https://somewhere.example.com/activate/me/?key='
        }
        rsp = self.api_client.post(url, data=data, format='json')
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'email': ['A user with that email already exists.']}, result)

    def test_create_provider_invalid_email(self):
        # Create provider call is made when user is NOT logged in.
        self.client.logout()

        url = '/api/providers/create_provider/'
        data = {
            'name_en': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description_en': 'Test provider',
            'email': 'this_is_not_an_email',
            'password': 'foobar',
            'number_of_monthly_beneficiaries': '37',
            'base_activation_link': 'https://somewhere.example.com/activate/me/?key='
        }
        rsp = self.api_client.post(url, data=data, format='json')
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'email': ['Enter a valid email address.']}, result)

    def test_create_provider_no_password(self):
        # Create provider call is made when user is NOT logged in.
        self.client.logout()

        url = '/api/providers/create_provider/'
        data = {
            'name_en': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description_en': 'Test provider',
            'email': 'fred@example.com',
            'number_of_monthly_beneficiaries': '37',
            'base_activation_link': 'https://somewhere.example.com/activate/me/?key='
        }
        rsp = self.api_client.post(url, data=data, format='json')
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        err = result['password'][0]
        self.assertIn(err, ['This field may not be blank.', 'This field is required.'])

    def test_create_provider_and_user(self):
        # Create provider call is made when user is NOT logged in.
        self.client.logout()

        url = '/api/providers/create_provider/'
        data = {
            'name_en': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description_en': 'Test provider',
            'email': 'fred@example.com',
            'password': 'foobar',
            'number_of_monthly_beneficiaries': '37',
            'base_activation_link': 'https://somewhere.example.com/activate/me/?key='
        }
        rsp = self.api_client.post(url, data=data, format='json')
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))

        # Make sure they gave us back the id of the new record
        result = json.loads(rsp.content.decode('utf-8'))
        provider = Provider.objects.get(id=result['id'])
        self.assertEqual('Joe Provider', provider.name_en)
        self.assertEqual(37, provider.number_of_monthly_beneficiaries)
        user = get_user_model().objects.get(id=provider.user_id)
        self.assertFalse(user.is_active)
        self.assertTrue(user.activation_key)
        # We should have sent an activation email
        self.assertEqual(len(mail.outbox), 1)
        # with a link
        link = user.get_activation_link(data['base_activation_link'])
        self.assertIn(link, mail.outbox[0].body)
        # user is not active
        self.assertFalse(provider.user.is_active)

    def test_get_provider_list(self):
        p1 = ProviderFactory()
        p2 = ProviderFactory()
        url = reverse('provider-list')
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        for item in result['results']:
            provider = Provider.objects.get(id=item['id'])
            self.assertIn(provider.name_en, [p1.name_en, p2.name_en])

    def test_get_one_provider(self):
        p1 = ProviderFactory(user=self.user)
        url = reverse('provider-detail', args=[p1.id])
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(p1.name_en, result['name_en'])


class TokenAuthTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.token = Token.objects.get(user=self.user).key

    def test_get_one_provider(self):
        p1 = ProviderFactory(user=self.user)
        url = reverse('provider-detail', args=[p1.id])
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(p1.name_en, result['name_en'])

    def test_create_provider(self):
        url = reverse('provider-list')
        data = {
            'name': 'Joe Provider',
            'type': ProviderTypeFactory().get_api_url(),
            'phone_number': '12345',
            'description': 'Test provider',
            'user': self.user_url,
            'number_of_monthly_beneficiaries': '37',
        }
        rsp = self.post_with_token(url, data=data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))


class ServiceAPITest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.provider = ProviderFactory(user=self.user, name_en="Our provider")

    def test_create_service(self):
        area = ServiceAreaFactory()
        wrong_provider = ProviderFactory(name_en="Wrong provider")
        data = {
            'provider': wrong_provider.get_api_url(),  # should just be ignored
            'name_en': 'Some service',
            'area_of_service': area.get_api_url(),
            'description_en': "Awesome\nService",
            'type': ServiceTypeFactory().get_api_url(),
        }
        rsp = self.client.post(reverse('service-list'), data=data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        service = Service.objects.get(id=result['id'])
        self.assertEqual('Some service', service.name_en)
        self.assertEqual(self.provider, service.provider)

    def test_get_service(self):
        service = ServiceFactory(provider=self.provider)
        rsp = self.client.get(service.get_api_url())
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(service.pk, result['id'])

    def test_get_services(self):
        # Should only get user's own services
        provider = self.provider
        s1 = ServiceFactory(provider=provider)
        s2 = ServiceFactory(provider=provider)
        other_provider = ProviderFactory()
        s3 = ServiceFactory(provider=other_provider)
        rsp = self.client.get(reverse('service-list'))
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        services = result['results']
        service_ids = [x['id'] for x in services]
        self.assertEqual(2, len(services))
        self.assertIn(s1.id, service_ids)
        self.assertIn(s2.id, service_ids)
        self.assertNotIn(s3.id, service_ids)


class SelectionCriterionAPITest(APITestMixin, TestCase):
    def test_create_selection_criterion(self):
        rsp = self.client.post(reverse('selectioncriterion-list'),
                               data={
                                   'text_en': 'English',
                                   'text_ar': '',
                                   'text_fr': '',
                                   })
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        criterion = SelectionCriterion.objects.get(id=result['id'])
        self.assertEqual('English', criterion.text_en)

    def test_get_selection_criteria(self):
        # Only returns user's own selection criteria
        # Defined as those attached to the user's services
        service = ServiceFactory(provider__user=self.user)
        s1 = SelectionCriterionFactory()
        s2 = SelectionCriterionFactory()
        service.selection_criteria.add(s1, s2)
        other_provider = ProviderFactory()
        other_service = ServiceFactory(provider=other_provider)
        s3 = SelectionCriterionFactory()
        other_service.selection_criteria.add(s3)
        rsp = self.client.get(reverse('selectioncriterion-list'))
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        criteria = result['results']
        criteria_ids = [x['id'] for x in criteria]
        self.assertEqual(2, len(criteria))
        self.assertIn(s1.id, criteria_ids)
        self.assertIn(s2.id, criteria_ids)
        self.assertNotIn(s3.id, criteria_ids)


class ServiceAreaAPITest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.area1 = ServiceAreaFactory()
        self.area2 = ServiceAreaFactory(parent=self.area1)
        self.area3 = ServiceAreaFactory(parent=self.area1)

    def test_get_areas(self):
        rsp = self.client.get(reverse('servicearea-list'))
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        results = result['results']
        names = [area.name_en for area in [self.area1, self.area2, self.area3]]
        for item in results:
            self.assertIn(item['name_en'], names)

    def test_get_area(self):
        rsp = self.client.get(self.area1.get_api_url())
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(self.area1.id, result['id'])
        self.assertIn('http://testserver%s' % self.area2.get_api_url(), result['children'])
        self.assertIn('http://testserver%s' % self.area3.get_api_url(), result['children'])
        rsp = self.client.get(self.area2.get_api_url())
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual('http://testserver%s' % self.area1.get_api_url(), result['parent'])


class LoginTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.token = Token.objects.get(user=self.user).key

    def test_success(self):
        # Call the API with the mail and password
        # Should get back the user's auth token
        rsp = self.client.post(reverse('api-login'),
                               data={'email': self.user.email, 'password': 'password'})
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(self.token, result['token'])

    def test_disabled_account(self):
        self.user.is_active = False
        self.user.save()
        rsp = self.client.post(reverse('api-login'),
                               data={'email': self.user.email, 'password': 'password'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'non_field_errors': ['User account is disabled.']}, response)

    def test_bad_call(self):
        # Call the API with username/password instead of email/password
        rsp = self.client.post(reverse('api-login'),
                               data={'username': 'Joe Sixpack', 'password': 'not_password'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'email': ['This field may not be blank.']}, response)

    def test_bad_password(self):
        # Call the API with a bad password
        rsp = self.client.post(reverse('api-login'),
                               data={'email': self.user.email, 'password': 'not_password'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'non_field_errors': ['Unable to log in with provided credentials.']},
                         response)

    def test_no_email(self):
        # Call the API without an email address
        rsp = self.client.post(reverse('api-login'),
                               data={'password': 'password'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'email': ['This field may not be blank.']},
                         response)

    def test_no_password(self):
        # Call the API without a password
        rsp = self.client.post(reverse('api-login'),
                               data={'email': self.user.email})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'password': ['This field may not be blank.']},
                         response)


class ResendActivationLinkTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        # An inactive user/provider
        self.user.is_active = False
        self.user.activation_key = self.user.create_activation_key()
        self.user.save()
        self.url = reverse('resend-activation-link')

    def test_successful_resend(self):
        rsp = self.client.post(self.url,
                               data={'email': self.user.email,
                                     'base_activation_link': 'http://example.com/foo?'})
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))

    def test_already_activated(self):
        EmailUser.objects.activate_user(self.user.activation_key)
        rsp = self.client.post(self.url,
                               data={'email': self.user.email,
                                     'base_activation_link': 'http://example.com/foo?'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response,
                         {"email": ["User is not pending activation"]})

    def test_no_inactive_user(self):
        rsp = self.client.post(self.url,
                               data={'email': 'nonesuch@example.com',
                                     'base_activation_link': 'http://example.com/foo?'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'email': ['No user with that email']},
                         response)

    def test_invalid_email(self):
        rsp = self.client.post(self.url,
                               data={'email': 'nonesuch.example.com',
                                     'base_activation_link': 'http://example.com/foo?'})
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual({'email': ['Enter a valid email address.']},
                         response)


class ActivationTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user.is_active = False
        self.user.activation_key = self.user.create_activation_key()
        self.user.save()
        self.url = reverse('api-activate')

    def test_basic_activation(self):
        rsp = self.client.post(
            path=self.url,
            data={'activation_key': self.user.activation_key}
        )
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        # Make sure the user is now active
        self.user = EmailUser.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.is_active)
        # Make sure we get back a token
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertIn('token', result)
        self.token = result['token']

        # Make sure it's the right token
        token_object = Token.objects.get(user=self.user)
        self.assertEqual(self.token, token_object.key)

        # Should also get back the user's email
        self.assertEqual(self.user.email, result['email'])

        # Make sure the token works - make user superuser just for simplicity
        self.user.is_superuser = True
        self.user.save()
        p1 = ProviderFactory(user=self.user)
        url = reverse('provider-detail', args=[p1.id])
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))

    def test_already_activated(self):
        # Save the key
        key = self.user.activation_key
        # Activate the user
        rsp = self.client.post(
            path=self.url,
            data={'activation_key': self.user.activation_key}
        )
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        # Now activate them again - should fail
        rsp = self.client.post(
            path=self.url,
            data={'activation_key': key}
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response, {'activation_key': [
            'Activation key is invalid. Check that it was copied correctly '
            'and has not already been used.']})

    def test_not_passing_key(self):
        rsp = self.client.post(
            path=self.url,
            data={}
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response, {'activation_key': ['This field may not be blank.']})

    def test_empty_key(self):
        rsp = self.client.post(
            path=self.url,
            data={'activation_key': ''}
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response, {'activation_key': ['This field may not be blank.']})

    def test_bad_key_format(self):
        rsp = self.client.post(
            path=self.url,
            data={'activation_key': 'not a sha1 string'}
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response, {'activation_key': [
            'Activation key is invalid. Check that it was copied correctly '
            'and has not already been used.']})


class PasswordResetTest(APITestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.first_password = self.password
        self.assertEqual(self.user,
                         authenticate(email=self.user.email, password=self.first_password))
        self.request_url = reverse('password-reset-request')
        self.check_url = reverse('password-reset-check')
        self.reset_url = reverse('password-reset')

    def test_valid_request(self):
        base_link = 'https://example.com/reset?key='
        rsp = self.client.post(
            path=self.request_url,
            data={'email': self.user.email,
                  'base_reset_link': base_link}
        )
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        self.assertEqual(1, len(mail.outbox))
        msg = mail.outbox[0]
        self.assertIn(base_link, msg.body)

    def test_request_no_such_user(self):
        base_link = 'https://example.com/reset?key='
        rsp = self.client.post(
            path=self.request_url,
            data={'email': 'nonesuch@example.com',
                  'base_reset_link': base_link}
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response,
                         {"email": ["No user with that email"]})

    def test_check_valid_key(self):
        key = self.user.get_password_reset_key()
        rsp = self.client.post(
            path=self.check_url,
            data={
                'email': self.user.email,
                'key': key,
            }
        )
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))

    def test_check_invalid_key(self):
        key = self.user.get_password_reset_key() + "broken"
        rsp = self.client.post(
            path=self.check_url,
            data={
                'email': self.user.email,
                'key': key,
            }
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response,
                         {"non_field_errors": ["Password reset key is not valid"]})

    def test_reset(self):
        key = self.user.get_password_reset_key()
        new_password = 'newpass'
        rsp = self.client.post(
            path=self.reset_url,
            data={
                'key': key,
                'password': new_password,
            }
        )
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response['email'], self.user.email)
        self.token = response['token']
        self.check_token()
        # New password works
        self.assertEqual(self.user,
                         authenticate(email=self.user.email, password=new_password))
        # Old one doesn't
        self.assertIsNone(authenticate(email=self.user.email, password=self.first_password))

    def test_reset_no_such_user(self):
        user2 = EmailUserFactory()
        key = user2.get_password_reset_key()
        user2.delete()
        new_password = 'newpass'
        rsp = self.client.post(
            path=self.reset_url,
            data={
                'key': key,
                'password': new_password,
            }
        )
        self.assertEqual(BAD_REQUEST, rsp.status_code, msg=rsp.content.decode('utf-8'))
        response = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(response,
                         {"non_field_errors": ["Password reset key is not valid"]})
