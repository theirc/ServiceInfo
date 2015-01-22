from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from email_user.models import EmailUser
from email_user.tests.factories import EmailUserFactory


class UserActivationTest(TestCase):
    def setUp(self):
        self.user = EmailUserFactory(is_active=False)
        self.user.activation_key = self.user.create_activation_key()
        self.user.save()

    def test_basic_activation(self):
        activated_user = EmailUser.objects.activate_user(self.user.activation_key)
        self.assertEqual(self.user.pk, activated_user.pk)
        user = EmailUser.objects.get(pk=self.user.pk)
        self.assertTrue(user.is_active)
        self.assertEqual(user.activation_key, EmailUser.ACTIVATED)

    def test_already_activated(self):
        self.user.is_active = True
        self.user.activation_key = EmailUser.ACTIVATED
        self.user.save()

        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user(self.user.activation_key)

    def test_wrong_key(self):
        another_key = self.user.create_activation_key()

        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user(another_key)

    def test_expired_key(self):
        self.user.date_joined = \
            self.user.date_joined - timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        self.user.save()

        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user(self.user.activation_key)
        # Also, the user should have been deleted
        self.assertFalse(EmailUser.objects.filter(pk=self.user.pk).exists())

    def test_bad_format(self):
        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user("not a sha1 string")
