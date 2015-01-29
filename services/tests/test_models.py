from django.test import TestCase
from django.utils import translation

from email_user.tests.factories import EmailUserFactory
from services.models import ServiceType, ProviderType, Provider, Service
from services.tests.factories import ProviderFactory


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
