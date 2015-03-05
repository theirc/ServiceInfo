from django.test import TestCase
from django.test.utils import override_settings
from email_user.forms import EmailUserCreationForm
from email_user.tests.factories import EmailUserFactory


class EmailUserCreationFormTest(TestCase):
    def test_valid(self):
        email = "user@example.com"

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'password',
             'password2': 'password'})
        self.assertTrue(form.is_valid())

    def test_email_not_valid(self):
        email = "user.example.com"

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'password',
             'password2': 'password'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    @override_settings(MINIMUM_PASSWORD_LENGTH=6)
    def test_password_too_short(self):
        email = "user@example.com"

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'passw',
             'password2': 'passw'})
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)

    def test_user_exists(self):
        email = "user@example.com"
        EmailUserFactory(email=email)

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'password',
             'password2': 'password'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
