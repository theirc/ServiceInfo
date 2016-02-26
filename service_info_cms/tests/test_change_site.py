import io

from django.test import TestCase

from cms.models import Page
from django.contrib.sites.models import Site
from django.core.management import call_command, CommandError

from email_user.tests.factories import EmailUserFactory
from service_info_cms import utils


class BaseMovePagesTest(TestCase):

    def setUp(self):
        self.user = EmailUserFactory(is_superuser=True)
        # Use the existing sites; their use of hard-coded pks breaks the ability to
        # add arbitrary additional sites for this test.
        self.orig_site_domain = 'serviceinfo.rescue.org'
        self.new_site_domain = 'serviceinfo-staging.rescue.org'
        self.orig_site = Site.objects.get(domain=self.orig_site_domain)
        self.new_site = Site.objects.get(domain=self.new_site_domain)
        utils.create_essential_pages(self.user, self.orig_site)

    def pre_move(self):
        starting_counts = {
            'orig_pages': Page.objects.filter(site=self.orig_site).count(),
            'new_pages': Page.objects.filter(site=self.new_site).count(),
        }
        self.assertEqual(0, starting_counts['new_pages'])
        self.assertGreater(starting_counts['orig_pages'], 0)
        return starting_counts

    def post_move(self, starting_counts):
        ending_counts = {
            'orig_pages': Page.objects.filter(site=self.orig_site).count(),
            'new_pages': Page.objects.filter(site=self.new_site).count(),
        }
        self.assertEqual(starting_counts['orig_pages'], ending_counts['new_pages'])
        self.assertEqual(ending_counts['new_pages'], starting_counts['orig_pages'])


class TestMovePagesFunction(BaseMovePagesTest):

    def test_move_function(self):
        starting_counts = self.pre_move()
        utils.change_cms_site(self.orig_site, self.new_site)
        self.post_move(starting_counts)


class TestMovePagesCommand(BaseMovePagesTest):

    def test_move_command(self):
        starting_counts = self.pre_move()
        hide_output = io.StringIO()
        call_command('change_cms_site', orig=self.orig_site_domain, to=self.new_site_domain,
                     stdout=hide_output)
        self.post_move(starting_counts)


class TestBadMovePagesCommands(BaseMovePagesTest):

    def test_same_domains(self):
        with self.assertRaises(CommandError):
            call_command('change_cms_site', orig=self.orig_site_domain, to=self.orig_site_domain)

    def test_only_one_domain(self):
        with self.assertRaises(CommandError):
            call_command('change_cms_site', orig=self.orig_site_domain)
