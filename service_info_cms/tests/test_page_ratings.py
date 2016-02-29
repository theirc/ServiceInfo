
from django.test import TestCase
from django.core.urlresolvers import reverse
import requests_mock

from cms.models import Page
from email_user.tests.factories import EmailUserFactory
from service_info_cms.models import PageRating
from service_info_cms.utils import create_essential_pages


class PageRatingsTest(TestCase):
    """
    Test the page ratings for good and bad POST values.
    """

    slug = 'update-page-rating'

    def setUp(self):
        self.user = EmailUserFactory(is_superuser=True)
        create_essential_pages(self.user)
        self.page = Page.objects.latest('id')
        self.pr = PageRating.objects.create(page_obj=self.page)
        self.pr.save()

    def test_good_page_rating(self):
        self.assertEqual(self.pr.average_rating, 0)
        self.assertEqual(self.pr.num_ratings, 0)
        parameters = {
            'rating': 3,
            'page_id': self.page.id,
            'return_url': self.page.get_absolute_url(language='en'),
            'g-recaptcha-response': 'anything',
        }
        with requests_mock.mock() as m:
            # Fake out backend verification of the CAPTCHA
            m.post(
                'https://www.google.com/recaptcha/api/siteverify',
                text='{"success": true}'
            )
            rsp = self.client.post(reverse(self.slug), parameters)
        self.assertRedirects(rsp, self.page.get_absolute_url(language='en'))
        pr = PageRating.objects.get(pk=self.pr.id)
        self.assertEqual(pr.average_rating, 3)
        self.assertEqual(pr.num_ratings, 1)

    def test_failed_captcha_verify(self):
        self.assertEqual(self.pr.average_rating, 0)
        self.assertEqual(self.pr.num_ratings, 0)
        parameters = {
            'rating': 3,
            'page_id': self.page.id,
            'return_url': self.page.get_absolute_url(language='en'),
            'g-recaptcha-response': 'anything',
        }
        with requests_mock.mock() as m:
            # Fake out backend verification of the CAPTCHA
            m.post(
                'https://www.google.com/recaptcha/api/siteverify',
                text='{"success": false}'
            )
            rsp = self.client.post(reverse(self.slug), parameters)
        self.assertEqual(500, rsp.status_code)
        pr = PageRating.objects.get(pk=self.pr.id)
        self.assertEqual(pr.average_rating, 0)
        self.assertEqual(pr.num_ratings, 0)

    def test_bad_page_rating(self):
        self.assertEqual(self.pr.average_rating, 0)
        self.assertEqual(self.pr.num_ratings, 0)
        parameters = {
            'rating': '',
            'page_id': self.page.id,
            'return_url': self.page.get_absolute_url(language='en')
        }
        self.client.post(reverse(self.slug), parameters)
        pr = PageRating.objects.get(pk=self.pr.id)
        self.assertEqual(pr.num_ratings, 0)
