from django.test import TestCase
from email_user.tests.factories import EmailUserFactory
from services.tests.factories import ProviderFactory


class TestProviderModel(TestCase):
    def test_related_name(self):
        # Just make sure we can get to the provider using user.provider
        user = EmailUserFactory()
        provider = ProviderFactory(
            user=user,
        )
        self.assertEqual(user.provider, provider)
