from django.test import TestCase
from email_user.forms import EmailUserCreationForm
from email_user.tests.factories import EmailUserFactory


class EmailUserCreationFormTest(TestCase):
    def test_valid(self):
        email = "user@example.com"

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'pass',
             'password2': 'pass'})
        self.assertTrue(form.is_valid())

    def test_email_not_valid(self):
        email = "user.example.com"

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'pass',
             'password2': 'pass'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_exists(self):
        email = "user@example.com"
        EmailUserFactory(email=email)

        form = EmailUserCreationForm(
            {'email': email,
             'password1': 'pass',
             'password2': 'pass'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
