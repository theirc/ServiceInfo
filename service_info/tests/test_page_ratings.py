from django.test import TestCase

from cms.models import Page
from email_user.tests.factories import EmailUserFactory
from service_info_cms.utils import create_essential_pages


class PageRatingsTest(TestCase):
    """
    Test the page ratings for good and bad POST values.
    """

    url_name = 'update-page-rating'

    def setUp(self):
        password = 'abc123'
        user = EmailUserFactory(password=password)
        create_essential_pages(user)
        self.page = Page.objects.latest('id')

    def test_good_page_rating(self):
        self.assertEqual(self.page.average_rating, 0)
        self.assertEqual(self.page.num_ratings, 0)
        context = {'rating': 3,
                   'page_id': self.page.page_id,
                   'return_url': self.page.get_absolute_url(language='en')
                   }
        self.client.post(self.url(), context)
        page = Page.objects.latest('id')
        self.assertEqual(page.average_rating, 3)
        self.assertEqual(page.num_ratings, 1)

    def test_bad_page_rating(self):
        self.assertEqual(self.page.average_rating, 0)
        self.assertEqual(self.page.num_ratings, 0)
        context = {'rating': '',
                   'page_id': self.page.page_id,
                   'return_url': self.page.get_absolute_url(language='en')
                   }
        self.client.post(self.url(), context)
        page = Page.objects.latest('id')
        self.assertEqual(page.average_rating, 0)
        self.assertEqual(page.num_ratings, 0)
