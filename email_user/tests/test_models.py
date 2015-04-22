from unittest.mock import patch
from django.core import mail
from django.core.exceptions import ValidationError
from django.template import Template
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
        key = self.user.activation_key
        EmailUser.objects.activate_user(key)
        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user(key)

    def test_wrong_key(self):
        another_key = self.user.create_activation_key()

        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user(another_key)

    def test_bad_format(self):
        with self.assertRaises(ValidationError):
            EmailUser.objects.activate_user("not a sha1 string")

    def test_send_email_to_user(self):
        # send_email_to_user() submits mail to Django and translates its content
        # We'll include a string in the template that we know Django has translated:
        english_text = "Are you sure?"
        french_text = "Êtes-vous sûr\xa0?"
        arabic_text = "هل أنت متأكد؟"

        our_template = Template('{% load i18n %}{% trans "' + english_text + '" %}')

        for lang, expected_text in [('', english_text), ('fr', french_text), ('ar', arabic_text),
                                    ('en', english_text)]:
            self.user.language = lang
            self.user.save()
            with patch('django.template.loader.get_template') as mock_get_template:
                mock_get_template.return_value = our_template
                self.user.send_email_to_user({}, '', '', '')

            # Test that one message has been sent.
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(expected_text, mail.outbox[0].body)
            # Empty the test outbox
            mail.outbox = []

    def test_unique_emails(self):
        # Users' emails must be unique, case-insensitively
        user1 = EmailUserFactory()
        with self.assertRaises(ValidationError):
            EmailUserFactory(email=user1.email.upper())
