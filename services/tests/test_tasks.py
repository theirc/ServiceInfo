from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase, override_settings

from email_user.tests.factories import EmailUserFactory
from services.tasks import email_provider_about_service_approval_task
from services.tests.factories import ProviderFactory, ServiceFactory


class ServiceApprovalEmailTaskTest(TestCase):
    def setUp(self):
        self.user = EmailUserFactory()
        self.provider = ProviderFactory(user=self.user)
        self.service = ServiceFactory(provider=self.provider)

    def test_email_task_calls_email_send(self):
        site = Site.objects.create(domain='example.com')
        with override_settings(SITE_ID=site.id, SECURE_LINKS=True):
            with patch('email_user.models.EmailUser.send_email_to_user') as mock_send:
                email_provider_about_service_approval_task(self.service.pk)
        expected_link = 'https://example.com/app/#/service/%d' % (self.service.pk,)
        mock_send.assert_called_with(
            {
                'site': site,
                'service': self.service,
                'provider': self.provider,
                'user': self.user,
                'service_link': expected_link,
            },
            'email/service_approved_subject.txt',
            'email/service_approved_body.txt',
            'email/service_approved_body.html',
        )

    def test_email_task_sends_email(self):
        email_provider_about_service_approval_task(self.service.pk)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Service has been approved IRC ServiceInfo Dev')

        # Make this fancier later - probably just want to make sure that it has
        # the name of the service or something. Maybe test translation too.
        body = mail.outbox[0].body
        self.assertIn("Your service", body)
        self.assertIn(self.service.name_en, body)
        self.assertIn(self.provider.name_en, body)
