from unittest.mock import patch

from django.test import TestCase
from django.utils import translation

from email_user.tests.factories import EmailUserFactory
from services.models import ServiceType, ProviderType, Provider, Service, \
    blank_or_at_least_one_letter
from services.tests.factories import ProviderFactory, ServiceFactory


class ProviderTest(TestCase):
    def test_related_name(self):
        # Just make sure we can get to the provider using user.provider
        user = EmailUserFactory()
        provider = ProviderFactory(
            user=user,
        )
        self.assertEqual(user.provider, provider)

    def test_str(self):
        # str returns name_en
        provider = Provider(name_en="Frederick")
        self.assertEqual("Frederick", str(provider))

    def test_blank_or_at_least_one_letter(self):
        data = [
            ('', True),
            ('1', False),
            ('1111', False),
            ('11111a', True),
            (' ', False),
            ('&', False),
            ('2 Men & a Truck', True),
        ]
        for input, expected_result in data:
            self.assertEqual(expected_result, blank_or_at_least_one_letter(input))


class ProviderTypeTest(TestCase):
    def test_str(self):
        # str() returns name in current language
        obj = ProviderType(name_en="English", name_ar="Arabic", name_fr="French")
        translation.activate('fr')
        self.assertEqual("French", str(obj))
        translation.activate('ar')
        self.assertEqual("Arabic", str(obj))
        translation.activate('en')
        self.assertEqual("English", str(obj))
        translation.activate('de')
        self.assertEqual("English", str(obj))


class ServiceTypeTest(TestCase):
    def test_str(self):
        # str() returns name in current language
        obj = ServiceType(name_en="English", name_ar="Arabic", name_fr="French")
        translation.activate('fr')
        self.assertEqual("French", str(obj))
        translation.activate('ar')
        self.assertEqual("Arabic", str(obj))
        translation.activate('en')
        self.assertEqual("English", str(obj))
        translation.activate('de')
        self.assertEqual("English", str(obj))


class ServiceTest(TestCase):
    def test_str(self):
        # str returns name_en
        service = Service(name_en="Frederick")
        self.assertEqual("Frederick", str(service))

    def test_email_provider_about_approval(self):
        service = ServiceFactory()
        with patch('services.models.email_provider_about_service_approval_task') as mock_task:
            service.email_provider_about_approval()
        mock_task.delay.assert_called_with(service.pk)
